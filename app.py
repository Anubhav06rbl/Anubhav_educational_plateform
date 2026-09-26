import os
import json
import uuid
import shutil
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Header, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Base Directory Setup
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure all directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
for sub in ["documents", "videos", "audio", "images", "slides"]:
    (UPLOADS_DIR / sub).mkdir(parents=True, exist_ok=True)

MATERIALS_FILE = DATA_DIR / "materials.json"
QUIZZES_FILE = DATA_DIR / "quizzes.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
USERS_FILE = DATA_DIR / "users.json"

# Thread locks for safe JSON reads and writes
file_locks = {
    MATERIALS_FILE: threading.Lock(),
    QUIZZES_FILE: threading.Lock(),
    SUBMISSIONS_FILE: threading.Lock(),
    USERS_FILE: threading.Lock()
}

def read_json(file_path: Path, default_val: Any = None) -> Any:
    lock = file_locks.setdefault(file_path, threading.Lock())
    with lock:
        if not file_path.exists():
            if default_val is not None:
                write_json(file_path, default_val)
                return default_val
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val if default_val is not None else []

def write_json(file_path: Path, data: Any):
    lock = file_locks.setdefault(file_path, threading.Lock())
    with lock:
        tmp_file = file_path.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_file.replace(file_path)

def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def detect_resource_type(filename: str, explicit_type: Optional[str] = None) -> str:
    if explicit_type and explicit_type.strip() in ["documents", "videos", "audio", "images", "slides"]:
        return explicit_type.strip()
    
    ext = Path(filename).suffix.lower()
    if ext in [".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv"]:
        return "videos"
    elif ext in [".mp3", ".wav", ".aac", ".flac", ".m4a", ".oga"]:
        return "audio"
    elif ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"]:
        return "images"
    elif ext in [".ppt", ".pptx", ".key"]:
        return "slides"
    else:
        return "documents"

# Initialize FastAPI App
app = FastAPI(
    title="EduSphere Learning Platform API",
    description="Full-stack Educational Platform API with Role-Based Access Control and One-Time Upload Passes.",
    version="1.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads and static directories
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ==========================================
# AUTHENTICATION & ACTIVE SESSIONS
# ==========================================
active_sessions: Dict[str, Dict[str, Any]] = {}

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return active_sessions.get(token)

def require_auth(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required. Please log in.")
    return user

def require_super_admin(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    user = require_auth(authorization)
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Super Admin privileges required.")
    return user

# ==========================================
# PYDANTIC MODELS
# ==========================================

class LoginRequest(BaseModel):
    identifier: Optional[str] = None # username or email
    password: Optional[str] = None
    one_time_pass: Optional[str] = None

class CreateTeacherRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    upload_type: str = "permanent" # "permanent" or "one_time"
    can_upload: bool = True

class UpdatePermissionsRequest(BaseModel):
    can_upload: Optional[bool] = None
    upload_type: Optional[str] = None

class CreateOneTimePassRequest(BaseModel):
    assigned_to: str # Name of teacher or guest

class QuestionItem(BaseModel):
    id: Optional[str] = None
    question: str
    options: List[str]
    correct_option_index: int
    points: int = 10
    explanation: Optional[str] = ""

class CreateQuizRequest(BaseModel):
    title: str
    category: str
    chapter: str
    description: str
    time_limit_minutes: int = 10
    questions: List[QuestionItem]

class QuizAnswerSubmission(BaseModel):
    question_id: str
    selected_option_index: int

class SubmitQuizPayload(BaseModel):
    student_name: str
    student_email: Optional[str] = ""
    answers: List[QuizAnswerSubmission]

# ==========================================
# PAGE ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def serve_student_portal():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Student portal template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin_portal():
    admin_file = TEMPLATES_DIR / "admin.html"
    if not admin_file.exists():
        raise HTTPException(status_code=404, detail="Admin portal template not found")
    with open(admin_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# ==========================================
# AUTHENTICATION API
# ==========================================

@app.post("/api/auth/login")
async def login(payload: LoginRequest):
    users_db = read_json(USERS_FILE, {})
    
    # 1. Login via One-Time Passcode
    if payload.one_time_pass and payload.one_time_pass.strip():
        pass_code = payload.one_time_pass.strip().upper()
        passes = users_db.get("one_time_passes", [])
        matched_pass = next((p for p in passes if p["token"].upper() == pass_code), None)
        
        if not matched_pass:
            raise HTTPException(status_code=400, detail="Invalid One-Time Pass code.")
        if matched_pass.get("status") == "used":
            raise HTTPException(status_code=400, detail="This One-Time Pass has already been used.")
            
        token = f"sess_otp_{uuid.uuid4().hex}"
        session_data = {
            "user_id": matched_pass["id"],
            "name": matched_pass.get("assigned_to", "Guest Teacher"),
            "email": "one_time_guest@campus.edu",
            "role": "one_time_teacher",
            "can_upload": True,
            "upload_type": "one_time",
            "pass_id": matched_pass["id"]
        }
        active_sessions[token] = session_data
        return {"status": "success", "token": token, "user": session_data}

    # 2. Login via Standard Username / Email + Password
    if not payload.identifier or not payload.password:
        raise HTTPException(status_code=400, detail="Please provide username/email and password, or a One-Time Pass.")

    ident = payload.identifier.strip().lower()
    pwd = payload.password.strip()

    # Check Super Admin
    super_admin = users_db.get("super_admin", {})
    admin_identifiers = [
        super_admin.get("email", "").lower(),
        super_admin.get("username", "").lower(),
        "anubhav"
    ]
    if (ident in admin_identifiers) and (pwd == super_admin.get("password_hash")):
        token = f"sess_admin_{uuid.uuid4().hex}"
        session_data = {
            "user_id": super_admin.get("id"),
            "name": super_admin.get("name"),
            "email": super_admin.get("email"),
            "username": super_admin.get("username"),
            "role": "super_admin",
            "can_upload": True,
            "upload_type": "permanent"
        }
        active_sessions[token] = session_data
        return {"status": "success", "token": token, "user": session_data}

    # Check Teachers
    teachers = users_db.get("users", [])
    matched_teacher = next((t for t in teachers if (ident in [t.get("email", "").lower(), t.get("username", "").lower()]) and (pwd == t.get("password_hash"))), None)

    if matched_teacher:
        if matched_teacher.get("status") == "revoked":
            raise HTTPException(status_code=403, detail="Your account has been deactivated by the Admin.")
            
        token = f"sess_teacher_{uuid.uuid4().hex}"
        session_data = {
            "user_id": matched_teacher.get("id"),
            "name": matched_teacher.get("name"),
            "email": matched_teacher.get("email"),
            "username": matched_teacher.get("username"),
            "role": "teacher",
            "can_upload": matched_teacher.get("can_upload", False),
            "upload_type": matched_teacher.get("upload_type", "permanent")
        }
        active_sessions[token] = session_data
        return {"status": "success", "token": token, "user": session_data}

    raise HTTPException(status_code=401, detail="Invalid credentials. Please verify your email/username and password.")

@app.get("/api/auth/me")
async def get_my_profile(authorization: Optional[str] = Header(None)):
    user = require_auth(authorization)
    # Refresh live permissions from database in case admin updated them
    users_db = read_json(USERS_FILE, {})
    if user.get("role") == "super_admin":
        user["can_upload"] = True
    elif user.get("role") == "teacher":
        db_user = next((t for t in users_db.get("users", []) if t["id"] == user["user_id"]), None)
        if db_user:
            user["can_upload"] = db_user.get("can_upload", False)
            user["upload_type"] = db_user.get("upload_type", "permanent")
    return {"status": "success", "data": user}

@app.post("/api/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        active_sessions.pop(token, None)
    return {"status": "success", "message": "Logged out successfully"}

# ==========================================
# SUPER ADMIN: USER & PERMISSION MANAGEMENT
# ==========================================

@app.get("/api/admin/users")
async def list_users(authorization: Optional[str] = Header(None)):
    require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    
    sanitized_users = []
    for u in users_db.get("users", []):
        sanitized_users.append({
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "username": u["username"],
            "role": u.get("role", "teacher"),
            "can_upload": u.get("can_upload", False),
            "upload_type": u.get("upload_type", "permanent"),
            "uploads_count": u.get("uploads_count", 0),
            "status": u.get("status", "active"),
            "created_at": u.get("created_at")
        })
        
    return {
        "status": "success",
        "super_admin": {
            "name": users_db.get("super_admin", {}).get("name"),
            "email": users_db.get("super_admin", {}).get("email")
        },
        "data": sanitized_users
    }

@app.post("/api/admin/users")
async def create_teacher_account(payload: CreateTeacherRequest, authorization: Optional[str] = Header(None)):
    require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    
    # Check duplicate
    for u in users_db.get("users", []):
        if u["email"].lower() == payload.email.strip().lower() or u["username"].lower() == payload.username.strip().lower():
            raise HTTPException(status_code=400, detail="Teacher with this email or username already exists.")

    new_id = f"usr_{uuid.uuid4().hex[:8]}"
    new_teacher = {
        "id": new_id,
        "name": payload.name.strip(),
        "email": payload.email.strip(),
        "username": payload.username.strip(),
        "password_hash": payload.password.strip(),
        "role": "teacher",
        "can_upload": payload.can_upload,
        "upload_type": payload.upload_type, # "permanent" or "one_time"
        "uploads_count": 0,
        "max_uploads": 1 if payload.upload_type == "one_time" else None,
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    users_db.setdefault("users", []).append(new_teacher)
    write_json(USERS_FILE, users_db)
    return {"status": "success", "message": f"Teacher account '{new_teacher['name']}' created successfully.", "data": new_teacher}

@app.patch("/api/admin/users/{user_id}/permissions")
async def update_user_permissions(user_id: str, payload: UpdatePermissionsRequest, authorization: Optional[str] = Header(None)):
    require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    
    user = next((u for u in users_db.get("users", []) if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if payload.can_upload is not None:
        user["can_upload"] = payload.can_upload
    if payload.upload_type is not None:
        user["upload_type"] = payload.upload_type
        if payload.upload_type == "one_time":
            user["max_uploads"] = 1
            user["uploads_count"] = 0
            
    write_json(USERS_FILE, users_db)
    return {"status": "success", "message": f"Permissions updated for '{user['name']}'.", "data": user}

@app.delete("/api/admin/users/{user_id}")
async def delete_teacher_account(user_id: str, authorization: Optional[str] = Header(None)):
    require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    
    users_list = users_db.get("users", [])
    index = next((i for i, u in enumerate(users_list) if u["id"] == user_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Teacher account not found.")
        
    deleted = users_list.pop(index)
    write_json(USERS_FILE, users_db)
    return {"status": "success", "message": f"Teacher account '{deleted.get('name')}' deleted successfully."}

# ==========================================
# SUPER ADMIN: ONE-TIME PASS MANAGEMENT
# ==========================================

@app.get("/api/admin/one-time-passes")
async def list_one_time_passes(authorization: Optional[str] = Header(None)):
    require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    passes = users_db.get("one_time_passes", [])
    passes.sort(key=lambda p: p.get("created_at", ""), reverse=True)
    return {"status": "success", "data": passes}

@app.post("/api/admin/one-time-passes")
async def create_one_time_pass(payload: CreateOneTimePassRequest, authorization: Optional[str] = Header(None)):
    admin = require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    
    token_code = f"PASS-{uuid.uuid4().hex[:6].upper()}"
    new_pass = {
        "id": f"pass_{uuid.uuid4().hex[:8]}",
        "token": token_code,
        "assigned_to": payload.assigned_to.strip() or "Guest Teacher",
        "status": "active",
        "created_by": admin.get("email"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "used_at": None,
        "uploaded_material_id": None
    }
    
    users_db.setdefault("one_time_passes", []).insert(0, new_pass)
    write_json(USERS_FILE, users_db)
    return {"status": "success", "message": f"One-Time Upload Pass generated: {token_code}", "data": new_pass}

@app.delete("/api/admin/one-time-passes/{pass_id}")
async def revoke_one_time_pass(pass_id: str, authorization: Optional[str] = Header(None)):
    require_super_admin(authorization)
    users_db = read_json(USERS_FILE, {})
    
    passes = users_db.get("one_time_passes", [])
    index = next((i for i, p in enumerate(passes) if p["id"] == pass_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Pass not found.")
        
    revoked = passes.pop(index)
    write_json(USERS_FILE, users_db)
    return {"status": "success", "message": f"One-Time Pass '{revoked.get('token')}' revoked."}

# ==========================================
# MATERIALS API (PROTECTED UPLOAD & DELETE)
# ==========================================

@app.get("/api/materials")
async def get_materials(
    category: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    materials = read_json(MATERIALS_FILE, [])
    
    filtered = materials
    if category and category.lower() != "all":
        filtered = [m for m in filtered if m.get("category", "").lower() == category.lower()]
        
    if resource_type and resource_type.lower() != "all":
        filtered = [m for m in filtered if m.get("resource_type", "").lower() == resource_type.lower()]
        
    if search:
        s = search.lower().strip()
        filtered = [
            m for m in filtered
            if s in m.get("title", "").lower()
            or s in m.get("chapter", "").lower()
            or s in m.get("description", "").lower()
            or any(s in tag.lower() for tag in m.get("tags", []))
            or s in m.get("category", "").lower()
        ]
        
    # Sort newest first
    filtered.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    return {"status": "success", "count": len(filtered), "data": filtered}

@app.get("/api/materials/{material_id}")
async def get_material_detail(material_id: str):
    materials = read_json(MATERIALS_FILE, [])
    material = next((m for m in materials if m["id"] == material_id), None)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"status": "success", "data": material}

@app.post("/api/materials")
async def upload_material(
    file: Optional[UploadFile] = File(None),
    external_url: Optional[str] = Form(None),
    title: str = Form(...),
    category: str = Form(...),
    chapter: str = Form(...),
    description: str = Form(...),
    tags: str = Form(""),
    resource_type: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None)
):
    # Security: Verify uploader identity & permissions
    user = require_auth(authorization)
    
    users_db = read_json(USERS_FILE, {})
    can_upload = False
    is_one_time = False

    if user.get("role") == "super_admin":
        can_upload = True
    elif user.get("role") == "one_time_teacher":
        pass_id = user.get("pass_id")
        matched_pass = next((p for p in users_db.get("one_time_passes", []) if p["id"] == pass_id), None)
        if matched_pass and matched_pass.get("status") == "active":
            can_upload = True
            is_one_time = True
        else:
            raise HTTPException(status_code=403, detail="Your One-Time Pass has already been used or expired.")
    else:
        db_user = next((t for t in users_db.get("users", []) if t["id"] == user["user_id"]), None)
        if db_user and db_user.get("can_upload", False):
            can_upload = True
            if db_user.get("upload_type") == "one_time":
                is_one_time = True
                
    if not can_upload:
        raise HTTPException(
            status_code=403, 
            detail="Upload permission denied. You do not currently have upload access. Please contact the Admin."
        )

    # Check whether a file or an external URL was provided
    is_link = False
    clean_url = external_url.strip() if external_url else ""

    if clean_url:
        is_link = True
        if not clean_url.startswith(("http://", "https://")):
            clean_url = "https://" + clean_url

        # Auto-detect resource type for external link if not explicitly set
        if not resource_type or resource_type.strip() == "":
            low_url = clean_url.lower()
            if any(k in low_url for k in ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com"]):
                chosen_type = "videos"
            elif any(k in low_url for k in ["slideshare.net", "canva.com", "docs.google.com/presentation"]):
                chosen_type = "slides"
            elif any(k in low_url for k in ["spotify.com", "soundcloud.com", "podcast"]):
                chosen_type = "audio"
            else:
                chosen_type = "documents"
        else:
            chosen_type = resource_type.strip()

        is_youtube = any(k in clean_url.lower() for k in ["youtube.com", "youtu.be"])
        filesize = 0
        filesize_formatted = "YouTube Video" if is_youtube else "Web Link"
        unique_filename = "External Link"
        original_name = clean_url
        file_url = clean_url

    elif file and file.filename:
        chosen_type = detect_resource_type(file.filename, resource_type)
        target_folder = UPLOADS_DIR / chosen_type
        target_folder.mkdir(parents=True, exist_ok=True)
        
        ext = Path(file.filename).suffix
        stem = Path(file.filename).stem
        safe_stem = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in stem)[:50]
        unique_filename = f"{safe_stem}_{uuid.uuid4().hex[:8]}{ext}"
        target_path = target_folder / unique_filename
        
        try:
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write file to disk: {str(e)}")
        finally:
            file.file.close()
            
        filesize = target_path.stat().st_size
        filesize_formatted = format_file_size(filesize)
        original_name = file.filename
        file_url = f"/uploads/{chosen_type}/{unique_filename}"
    else:
        raise HTTPException(status_code=400, detail="Please provide either a file to upload or an external web link.")

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    material_id = f"mat_{uuid.uuid4().hex[:10]}"
    material_entry = {
        "id": material_id,
        "title": title.strip(),
        "category": category.strip(),
        "chapter": chapter.strip(),
        "resource_type": chosen_type,
        "description": description.strip(),
        "tags": tag_list,
        "filename": unique_filename,
        "original_name": original_name,
        "file_url": file_url,
        "is_external_link": is_link,
        "filesize": filesize,
        "filesize_formatted": filesize_formatted,
        "uploaded_by": user.get("name"),
        "uploaded_at": datetime.utcnow().isoformat() + "Z"
    }
    
    materials = read_json(MATERIALS_FILE, [])
    materials.insert(0, material_entry)
    write_json(MATERIALS_FILE, materials)
    
    # Consume one-time quota if applicable!
    one_time_message = ""
    if is_one_time:
        if user.get("role") == "one_time_teacher":
            pass_id = user.get("pass_id")
            for p in users_db.get("one_time_passes", []):
                if p["id"] == pass_id:
                    p["status"] = "used"
                    p["used_at"] = datetime.utcnow().isoformat() + "Z"
                    p["uploaded_material_id"] = material_id
            user["can_upload"] = False
            one_time_message = " (Note: Your One-Time Pass has been successfully consumed.)"
        else:
            db_user = next((t for t in users_db.get("users", []) if t["id"] == user["user_id"]), None)
            if db_user:
                db_user["uploads_count"] = db_user.get("uploads_count", 0) + 1
                db_user["can_upload"] = False # Lock upload access after one-time upload!
                user["can_upload"] = False
                one_time_message = " (Your one-time upload has been used. Admin can renew permissions.)"
        write_json(USERS_FILE, users_db)
    
    return {
        "status": "success", 
        "message": f"Resource successfully uploaded by {user.get('name')}!{one_time_message}", 
        "data": material_entry
    }

@app.delete("/api/materials/{material_id}")
async def delete_material(material_id: str, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    materials = read_json(MATERIALS_FILE, [])
    index = next((i for i, m in enumerate(materials) if m["id"] == material_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Material not found")
        
    deleted_item = materials.pop(index)
    write_json(MATERIALS_FILE, materials)
    
    rel_path = deleted_item.get("file_url", "").lstrip("/uploads/")
    full_path = UPLOADS_DIR / rel_path
    if full_path.exists():
        try:
            full_path.unlink()
        except Exception:
            pass
            
    return {"status": "success", "message": f"Resource '{deleted_item.get('title')}' deleted successfully"}

@app.get("/api/materials/{material_id}/download")
async def download_material(material_id: str):
    materials = read_json(MATERIALS_FILE, [])
    item = next((m for m in materials if m["id"] == material_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Material not found")
        
    if item.get("is_external_link"):
        return RedirectResponse(url=item.get("file_url"))

    rel_path = item.get("file_url", "").replace("/uploads/", "")
    file_path = UPLOADS_DIR / rel_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found on disk")
        
    download_filename = item.get("original_name") or item.get("filename")
    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type="application/octet-stream"
    )

@app.get("/api/categories")
async def get_categories():
    materials = read_json(MATERIALS_FILE, [])
    category_counts = {}
    for m in materials:
        cat = m.get("category", "General")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
    cat_list = [{"name": cat, "count": count} for cat, count in sorted(category_counts.items())]
    return {"status": "success", "data": cat_list}

@app.get("/api/stats")
async def get_platform_stats():
    materials = read_json(MATERIALS_FILE, [])
    quizzes = read_json(QUIZZES_FILE, [])
    submissions = read_json(SUBMISSIONS_FILE, [])
    
    type_counts = {"documents": 0, "videos": 0, "audio": 0, "images": 0, "slides": 0}
    for m in materials:
        t = m.get("resource_type", "documents")
        if t in type_counts:
            type_counts[t] += 1
            
    avg_score = 0.0
    if submissions:
        avg_score = round(sum(s.get("percentage", 0) for s in submissions) / len(submissions), 1)
        
    return {
        "status": "success",
        "data": {
            "total_materials": len(materials),
            "total_quizzes": len(quizzes),
            "total_submissions": len(submissions),
            "average_score": avg_score,
            "type_counts": type_counts
        }
    }

# ==========================================
# QUIZZES API
# ==========================================

@app.get("/api/quizzes")
async def get_quizzes(category: Optional[str] = Query(None)):
    quizzes = read_json(QUIZZES_FILE, [])
    if category and category.lower() != "all":
        quizzes = [q for q in quizzes if q.get("category", "").lower() == category.lower()]
        
    sanitized = []
    for q in quizzes:
        sanitized_questions = []
        for quest in q.get("questions", []):
            sanitized_questions.append({
                "id": quest["id"],
                "question": quest["question"],
                "options": quest["options"],
                "points": quest.get("points", 10)
            })
        sanitized.append({
            "id": q["id"],
            "title": q["title"],
            "category": q["category"],
            "chapter": q["chapter"],
            "description": q["description"],
            "time_limit_minutes": q.get("time_limit_minutes", 10),
            "total_points": q.get("total_points", sum(qst.get("points", 10) for qst in q.get("questions", []))),
            "question_count": len(q.get("questions", [])),
            "created_at": q.get("created_at")
        })
    return {"status": "success", "count": len(sanitized), "data": sanitized}

@app.get("/api/quizzes/{quiz_id}")
async def get_quiz_for_taker(quiz_id: str):
    quizzes = read_json(QUIZZES_FILE, [])
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    sanitized_questions = []
    for quest in quiz.get("questions", []):
        sanitized_questions.append({
            "id": quest["id"],
            "question": quest["question"],
            "options": quest["options"],
            "points": quest.get("points", 10)
        })
        
    return {
        "status": "success",
        "data": {
            "id": quiz["id"],
            "title": quiz["title"],
            "category": quiz["category"],
            "chapter": quiz["chapter"],
            "description": quiz["description"],
            "time_limit_minutes": quiz.get("time_limit_minutes", 10),
            "total_points": quiz.get("total_points", sum(q.get("points", 10) for q in quiz.get("questions", []))),
            "questions": sanitized_questions
        }
    }

@app.get("/api/admin/quizzes")
async def get_admin_quizzes(authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    quizzes = read_json(QUIZZES_FILE, [])
    return {"status": "success", "count": len(quizzes), "data": quizzes}

@app.get("/api/admin/quizzes/{quiz_id}")
async def get_admin_quiz_detail(quiz_id: str, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    quizzes = read_json(QUIZZES_FILE, [])
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"status": "success", "data": quiz}

@app.post("/api/quizzes")
async def create_quiz(payload: CreateQuizRequest, authorization: Optional[str] = Header(None)):
    user = require_auth(authorization)
    if not payload.questions:
        raise HTTPException(status_code=400, detail="Quiz must contain at least one question")
        
    total_pts = 0
    formatted_questions = []
    for idx, q in enumerate(payload.questions, 1):
        if len(q.options) < 2:
            raise HTTPException(status_code=400, detail=f"Question {idx} must have at least 2 options")
        if q.correct_option_index < 0 or q.correct_option_index >= len(q.options):
            raise HTTPException(status_code=400, detail=f"Invalid correct option index for question {idx}")
            
        pts = q.points if q.points > 0 else 10
        total_pts += pts
        
        formatted_questions.append({
            "id": q.id or f"q_{uuid.uuid4().hex[:6]}",
            "question": q.question.strip(),
            "options": [opt.strip() for opt in q.options],
            "correct_option_index": q.correct_option_index,
            "points": pts,
            "explanation": q.explanation.strip() if q.explanation else ""
        })
        
    quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
    quiz_entry = {
        "id": quiz_id,
        "title": payload.title.strip(),
        "category": payload.category.strip(),
        "chapter": payload.chapter.strip(),
        "description": payload.description.strip(),
        "time_limit_minutes": max(1, payload.time_limit_minutes),
        "total_points": total_pts,
        "created_by": user.get("name"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "questions": formatted_questions
    }
    
    quizzes = read_json(QUIZZES_FILE, [])
    quizzes.insert(0, quiz_entry)
    write_json(QUIZZES_FILE, quizzes)
    
    return {"status": "success", "message": "Quiz created successfully", "data": quiz_entry}

@app.delete("/api/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    quizzes = read_json(QUIZZES_FILE, [])
    index = next((i for i, q in enumerate(quizzes) if q["id"] == quiz_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    deleted = quizzes.pop(index)
    write_json(QUIZZES_FILE, quizzes)
    return {"status": "success", "message": f"Quiz '{deleted.get('title')}' deleted successfully"}

@app.post("/api/quizzes/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, payload: SubmitQuizPayload):
    quizzes = read_json(QUIZZES_FILE, [])
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    student_name = payload.student_name.strip() or "Anonymous Student"
    student_email = payload.student_email.strip() if payload.student_email else ""
    
    questions_map = {q["id"]: q for q in quiz.get("questions", [])}
    answers_map = {a.question_id: a.selected_option_index for a in payload.answers}
    
    earned_points = 0
    total_points = quiz.get("total_points", sum(q.get("points", 10) for q in quiz.get("questions", [])))
    detailed_answers = []
    
    for q in quiz.get("questions", []):
        qid = q["id"]
        selected_idx = answers_map.get(qid, -1)
        correct_idx = q["correct_option_index"]
        q_pts = q.get("points", 10)
        
        is_correct = (selected_idx == correct_idx)
        points_awarded = q_pts if is_correct else 0
        earned_points += points_awarded
        
        detailed_answers.append({
            "question_id": qid,
            "question": q["question"],
            "options": q["options"],
            "selected_option_index": selected_idx,
            "correct_option_index": correct_idx,
            "is_correct": is_correct,
            "points_earned": points_awarded,
            "points_total": q_pts,
            "explanation": q.get("explanation", "")
        })
        
    pct = round((earned_points / total_points * 100), 1) if total_points > 0 else 0.0
    
    submission_id = f"sub_{uuid.uuid4().hex[:10]}"
    submission_entry = {
        "id": submission_id,
        "quiz_id": quiz_id,
        "quiz_title": quiz.get("title", "Untitled Quiz"),
        "student_name": student_name,
        "student_email": student_email,
        "score": earned_points,
        "total_points": total_points,
        "percentage": pct,
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "answers": [
            {
                "question_id": d["question_id"],
                "selected_option_index": d["selected_option_index"],
                "is_correct": d["is_correct"],
                "points_earned": d["points_earned"]
            }
            for d in detailed_answers
        ]
    }
    
    submissions = read_json(SUBMISSIONS_FILE, [])
    submissions.insert(0, submission_entry)
    write_json(SUBMISSIONS_FILE, submissions)
    
    return {
        "status": "success",
        "submission_id": submission_id,
        "student_name": student_name,
        "quiz_title": quiz.get("title"),
        "score": earned_points,
        "total_points": total_points,
        "percentage": pct,
        "breakdown": detailed_answers
    }

# ==========================================
# SUBMISSIONS API (TEACHER VIEW)
# ==========================================

@app.get("/api/submissions")
async def get_submissions(quiz_id: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    submissions = read_json(SUBMISSIONS_FILE, [])
    if quiz_id:
        submissions = [s for s in submissions if s.get("quiz_id") == quiz_id]
        
    submissions.sort(key=lambda s: s.get("submitted_at", ""), reverse=True)
    return {"status": "success", "count": len(submissions), "data": submissions}

@app.get("/api/submissions/{submission_id}")
async def get_submission_detail(submission_id: str, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    submissions = read_json(SUBMISSIONS_FILE, [])
    sub = next((s for s in submissions if s["id"] == submission_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission record not found")
        
    quizzes = read_json(QUIZZES_FILE, [])
    quiz = next((q for q in quizzes if q["id"] == sub.get("quiz_id")), None)
    
    enriched = dict(sub)
    if quiz:
        q_dict = {q["id"]: q for q in quiz.get("questions", [])}
        enriched_answers = []
        for a in sub.get("answers", []):
            qid = a.get("question_id")
            origin_q = q_dict.get(qid, {})
            enriched_answers.append({
                "question_id": qid,
                "question": origin_q.get("question", "Question prompt"),
                "options": origin_q.get("options", []),
                "selected_option_index": a.get("selected_option_index"),
                "correct_option_index": origin_q.get("correct_option_index"),
                "is_correct": a.get("is_correct"),
                "points_earned": a.get("points_earned"),
                "explanation": origin_q.get("explanation", "")
            })
        enriched["answers"] = enriched_answers
        
    return {"status": "success", "data": enriched}

@app.delete("/api/submissions/{submission_id}")
async def delete_submission(submission_id: str, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    submissions = read_json(SUBMISSIONS_FILE, [])
    index = next((i for i, s in enumerate(submissions) if s["id"] == submission_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    submissions.pop(index)
    write_json(SUBMISSIONS_FILE, submissions)
    return {"status": "success", "message": "Submission deleted"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    print(f"Starting EduSphere Educational Platform on http://{host}:{port} ...")
    uvicorn.run("app:app", host=host, port=port, reload=False)
