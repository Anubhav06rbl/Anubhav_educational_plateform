import os
import json
from io import BytesIO
from fastapi.testclient import TestClient
from app import app, MATERIALS_FILE, QUIZZES_FILE, SUBMISSIONS_FILE

client = TestClient(app)

def test_home_page():
    res = client.get("/")
    assert res.status_code == 200
    assert "EduSphere" in res.text
    print("[PASS] GET / (Student Portal) passed")

def test_admin_page():
    res = client.get("/admin")
    assert res.status_code == 200
    assert "Teacher & Admin Portal" in res.text
    print("[PASS] GET /admin (Admin Portal) passed")

def test_api_stats():
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "total_materials" in data["data"]
    assert "total_quizzes" in data["data"]
    print(f"[PASS] GET /api/stats passed: {data['data']['total_materials']} materials, {data['data']['total_quizzes']} quizzes")

def test_get_materials():
    res = client.get("/api/materials")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0
    print(f"[PASS] GET /api/materials returned {len(data['data'])} seeded items")

def test_get_categories():
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0
    print(f"[PASS] GET /api/categories returned {len(data['data'])} categories")

def test_upload_and_delete_material():
    dummy_content = b"This is a test lecture note on Thermodynamics.\nHeat transfer by conduction and radiation."
    files = {"file": ("test_thermodynamics.txt", BytesIO(dummy_content), "text/plain")}
    data = {
        "title": "Thermodynamics Revision Notes",
        "category": "Physics",
        "chapter": "Chapter 5: Heat & Thermodynamics",
        "description": "Comprehensive review of the first and second laws of thermodynamics.",
        "tags": "thermodynamics, heat, entropy",
        "resource_type": "documents"
    }
    res = client.post("/api/materials", data=data, files=files)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "success"
    mat_id = res_data["data"]["id"]
    print(f"[PASS] POST /api/materials created material {mat_id}")

    # Test download
    dl_res = client.get(f"/api/materials/{mat_id}/download")
    assert dl_res.status_code == 200
    assert b"Thermodynamics" in dl_res.content
    print("[PASS] GET /api/materials/{id}/download verified")

    # Test delete
    del_res = client.delete(f"/api/materials/{mat_id}")
    assert del_res.status_code == 200
    print(f"[PASS] DELETE /api/materials/{mat_id} verified")

def test_quiz_lifecycle():
    # 1. Get quizzes (student view)
    res = client.get("/api/quizzes")
    assert res.status_code == 200
    quizzes = res.json()["data"]
    assert len(quizzes) > 0
    quiz_id = quizzes[0]["id"]
    print(f"[PASS] GET /api/quizzes returned {len(quizzes)} quizzes")

    # 2. Detail quiz for taker
    taker_res = client.get(f"/api/quizzes/{quiz_id}")
    assert taker_res.status_code == 200
    quiz_detail = taker_res.json()["data"]
    # Check that answer keys are not leaked to student taker
    for q in quiz_detail["questions"]:
        assert "correct_option_index" not in q
    print("[PASS] GET /api/quizzes/{id} verified student sanitized questions")

    # 3. Submit quiz
    answers = []
    for q in quiz_detail["questions"]:
        answers.append({"question_id": q["id"], "selected_option_index": 1})
    
    sub_payload = {
        "student_name": "Test Runner",
        "student_email": "test.runner@campus.edu",
        "answers": answers
    }
    sub_res = client.post(f"/api/quizzes/{quiz_id}/submit", json=sub_payload)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["status"] == "success"
    assert "score" in sub_data
    assert "percentage" in sub_data
    assert len(sub_data["breakdown"]) == len(quiz_detail["questions"])
    print(f"[PASS] POST /api/quizzes/{quiz_id}/submit scored: {sub_data['score']}/{sub_data['total_points']} ({sub_data['percentage']}%)")

    # 4. Teacher inspect submissions
    subs_res = client.get("/api/submissions")
    assert subs_res.status_code == 200
    assert subs_res.json()["count"] > 0
    print(f"[PASS] GET /api/submissions returned {subs_res.json()['count']} submissions")

if __name__ == "__main__":
    print("Running platform automated tests...")
    test_home_page()
    test_admin_page()
    test_api_stats()
    test_get_materials()
    test_get_categories()
    test_upload_and_delete_material()
    test_quiz_lifecycle()
    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY! ALL ENDPOINTS VERIFIED.")

