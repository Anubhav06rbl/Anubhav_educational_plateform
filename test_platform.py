import os
import json
from io import BytesIO
from fastapi.testclient import TestClient
from app import app, MATERIALS_FILE, QUIZZES_FILE, SUBMISSIONS_FILE, USERS_FILE

client = TestClient(app)

def test_public_pages():
    res = client.get("/")
    assert res.status_code == 200
    assert "EduSphere" in res.text
    print("[PASS] GET / (Student Portal) loads publicly")

    res = client.get("/admin")
    assert res.status_code == 200
    assert "Authorized Portal Access" in res.text
    print("[PASS] GET /admin (Admin Gate) loads successfully")

def test_auth_and_super_admin():
    # 1. Login as Super Admin (Anubhav)
    res = client.post("/api/auth/login", json={"identifier": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["user"]["role"] == "super_admin"
    admin_token = data["token"]
    print("[PASS] Super Admin (Anubhav) login verified")

    # 2. Check /api/auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["data"]["role"] == "super_admin"
    print("[PASS] GET /api/auth/me authenticated successfully")

    return admin_token

def test_upload_privacy_protection(admin_token):
    dummy_file = ("unauthorized_test.txt", BytesIO(b"Secret educational note"), "text/plain")
    data = {
        "title": "Unauthorized Upload Attempt",
        "category": "Physics",
        "chapter": "Chapter 1",
        "description": "This should be blocked without credentials.",
        "resource_type": "documents"
    }

    # 1. Try uploading without any token -> Must return 401 Unauthorized
    res_no_auth = client.post("/api/materials", data=data, files={"file": dummy_file})
    assert res_no_auth.status_code == 401
    print("[PASS] Privacy Check: Unauthenticated upload attempt blocked with 401 Unauthorized")

    # 2. Upload with Super Admin token -> Must succeed
    dummy_file_admin = ("admin_upload.txt", BytesIO(b"Approved Admin Content"), "text/plain")
    res_admin = client.post("/api/materials", data=data, files={"file": dummy_file_admin}, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    mat_id = res_admin.json()["data"]["id"]
    print("[PASS] Super Admin authorized upload succeeded")

    # Cleanup test upload
    client.delete(f"/api/materials/{mat_id}", headers={"Authorization": f"Bearer {admin_token}"})

def test_external_link_upload(admin_token):
    link_data = {
        "title": "Quantum Mechanics MIT OpenCourseWare Video Lecture",
        "category": "Physics",
        "chapter": "Unit 3",
        "description": "Comprehensive video lecture on YouTube by MIT.",
        "external_url": "https://www.youtube.com/watch?v=lZ3bPUKo5zc",
        "tags": "quantum, youtube, mit",
        "resource_type": "videos"
    }
    res = client.post("/api/materials", data=link_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    mat = res.json()["data"]
    assert mat["is_external_link"] is True
    assert mat["file_url"] == "https://www.youtube.com/watch?v=lZ3bPUKo5zc"
    assert mat["filesize_formatted"] == "YouTube Video"
    print("[PASS] External Web Link / YouTube upload succeeded and verified")

    # Verify download redirect
    dl_res = client.get(f"/api/materials/{mat['id']}/download", follow_redirects=False)
    assert dl_res.status_code in (302, 307)
    assert dl_res.headers["location"] == "https://www.youtube.com/watch?v=lZ3bPUKo5zc"
    print("[PASS] External Link download endpoint properly redirects to external URL")

    # Cleanup
    client.delete(f"/api/materials/{mat['id']}", headers={"Authorization": f"Bearer {admin_token}"})

def test_one_time_teacher_lifecycle(admin_token):
    # 1. Super Admin registers a teacher with upload_type="one_time"
    new_teacher_data = {
        "name": "Guest Lecturer Dr. Ray",
        "email": "dr.ray@campus.edu",
        "username": "drray",
        "password": "pass_ray_123",
        "upload_type": "one_time",
        "can_upload": True
    }
    create_res = client.post("/api/admin/users", json=new_teacher_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_res.status_code == 200
    print("[PASS] Super Admin created teacher with One-Time upload privilege")

    # 2. Teacher logs in
    login_res = client.post("/api/auth/login", json={"identifier": "drray", "password": "pass_ray_123"})
    assert login_res.status_code == 200
    teacher_token = login_res.json()["token"]
    assert login_res.json()["user"]["can_upload"] is True

    # 3. Teacher performs their 1 allowed upload
    file1 = ("lecture1_ray.txt", BytesIO(b"Dr. Ray's Special One-Time Lecture"), "text/plain")
    up1_data = {
        "title": "Dr. Ray Special Lecture",
        "category": "Physics",
        "chapter": "Unit 2",
        "description": "Special invited talk.",
        "resource_type": "documents"
    }
    up1_res = client.post("/api/materials", data=up1_data, files={"file": file1}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert up1_res.status_code == 200
    print("[PASS] One-Time Teacher first upload succeeded")
    mat_id = up1_res.json()["data"]["id"]

    # 4. Teacher attempts a SECOND upload -> MUST BE BLOCKED with 403 Forbidden!
    file2 = ("lecture2_ray.txt", BytesIO(b"Second unauthorized attempt"), "text/plain")
    up2_res = client.post("/api/materials", data=up1_data, files={"file": file2}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert up2_res.status_code == 403
    assert "permission denied" in up2_res.json()["detail"].lower()
    print("[PASS] Privacy Check: Second upload by One-Time Teacher blocked with 403 Forbidden")

    # 5. Super Admin renews permission for Dr. Ray
    user_id = create_res.json()["data"]["id"]
    patch_res = client.patch(f"/api/admin/users/{user_id}/permissions", json={"can_upload": True}, headers={"Authorization": f"Bearer {admin_token}"})
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["can_upload"] is True
    print("[PASS] Super Admin successfully renewed upload permission for teacher")

    # Cleanup
    client.delete(f"/api/materials/{mat_id}", headers={"Authorization": f"Bearer {admin_token}"})
    client.delete(f"/api/admin/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})

def test_one_time_passcode_lifecycle(admin_token):
    # 1. Super Admin generates a One-Time Passcode
    pass_res = client.post("/api/admin/one-time-passes", json={"assigned_to": "Visiting Scholar"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert pass_res.status_code == 200
    pass_data = pass_res.json()["data"]
    pass_code = pass_data["token"]
    print(f"[PASS] Super Admin generated One-Time Passcode: {pass_code}")

    # 2. Visiting Scholar uses the One-Time Pass to login
    login_res = client.post("/api/auth/login", json={"one_time_pass": pass_code})
    assert login_res.status_code == 200
    guest_token = login_res.json()["token"]
    assert login_res.json()["user"]["role"] == "one_time_teacher"
    print("[PASS] Guest successfully signed in with One-Time Pass")

    # 3. Guest uploads 1 file
    f = ("scholar_notes.txt", BytesIO(b"Scholar Notes Content"), "text/plain")
    up_data = {
        "title": "Scholar Notes",
        "category": "Biology",
        "chapter": "Chapter 3",
        "description": "Guest material.",
        "resource_type": "documents"
    }
    up_res = client.post("/api/materials", data=up_data, files={"file": f}, headers={"Authorization": f"Bearer {guest_token}"})
    assert up_res.status_code == 200
    mat_id = up_res.json()["data"]["id"]
    print("[PASS] Guest uploaded file with One-Time Pass")

    # 4. Guest attempts to upload again with same session -> Blocked with 403!
    up_again = client.post("/api/materials", data=up_data, files={"file": ("again.txt", BytesIO(b"Test"), "text/plain")}, headers={"Authorization": f"Bearer {guest_token}"})
    assert up_again.status_code == 403
    print("[PASS] Subsequent upload blocked after pass was consumed")

    # 5. Someone tries to login again using the consumed pass code -> Blocked!
    re_login = client.post("/api/auth/login", json={"one_time_pass": pass_code})
    assert re_login.status_code == 400
    assert "already been used" in re_login.json()["detail"].lower()
    print("[PASS] Re-login with consumed One-Time Passcode blocked")

    # Cleanup
    client.delete(f"/api/materials/{mat_id}", headers={"Authorization": f"Bearer {admin_token}"})

def test_branch_taxonomy_filtering():
    # 1. Test GET /api/categories returns 4 branches
    res = client.get("/api/categories")
    assert res.status_code == 200
    res_json = res.json()
    taxonomy = res_json.get("taxonomy", {})
    assert "Computer Science" in taxonomy
    assert "Science" in taxonomy
    assert "Mathematics" in taxonomy["Science"]
    assert "Humanities" in taxonomy
    assert "Other" in taxonomy
    print("[PASS] GET /api/categories returns all 4 branches with sub-categories including Mathematics")

    # 2. Test GET /api/materials?branch=Science
    res_sci = client.get("/api/materials?branch=Science")
    assert res_sci.status_code == 200
    materials_sci = res_sci.json()["data"]
    assert all(m.get("branch") == "Science" for m in materials_sci)
    assert len(materials_sci) > 0
    print("[PASS] Branch filter 'Science' returned matching materials")

    # 3. Test GET /api/materials?branch=Science&sub_category=Mathematics
    res_math = client.get("/api/materials?branch=Science&sub_category=Mathematics")
    assert res_math.status_code == 200
    materials_math = res_math.json()["data"]
    assert len(materials_math) > 0
    assert all(m.get("sub_category") == "Mathematics" for m in materials_math)
    print("[PASS] Sub-category filter 'Mathematics' in 'Science' verified")

    # 4. Test GET /api/materials?branch=Computer Science&sub_category=Python
    res_py = client.get("/api/materials?branch=Computer%20Science&sub_category=Python")
    assert res_py.status_code == 200
    materials_py = res_py.json()["data"]
    assert all("python" in m.get("sub_category", "").lower() for m in materials_py)
    print("[PASS] Sub-category filter 'Python' in 'Computer Science' verified")

if __name__ == "__main__":
    print("Running EduSphere Access Control & Privacy Test Suite...\n")
    test_public_pages()
    test_branch_taxonomy_filtering()
    admin_token = test_auth_and_super_admin()
    test_upload_privacy_protection(admin_token)
    test_external_link_upload(admin_token)
    test_one_time_teacher_lifecycle(admin_token)
    test_one_time_passcode_lifecycle(admin_token)
    print("\nALL PRIVACY, TAXONOMY & ACCESS CONTROL TESTS PASSED (100% SUCCESS)!")
