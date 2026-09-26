import os
import json
import uuid
import shutil
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
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

# Thread locks for safe JSON reads and writes
file_locks = {
    MATERIALS_FILE: threading.Lock(),
    QUIZZES_FILE: threading.Lock(),
    SUBMISSIONS_FILE: threading.Lock()
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
    description="Full-stack Educational Platform API for materials, viewers, quizzes, and grading.",
    version="1.0.0"
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
# PYDANTIC MODELS
# ==========================================

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
# MATERIALS API
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
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    chapter: str = Form(...),
    description: str = Form(...),
    tags: str = Form(""),
    resource_type: Optional[str] = Form(None)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename provided")
        
    # Determine resource folder & categorization
    chosen_type = detect_resource_type(file.filename, resource_type)
    target_folder = UPLOADS_DIR / chosen_type
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Generate unique, clean filename while preserving extension
    ext = Path(file.filename).suffix
    stem = Path(file.filename).stem
    safe_stem = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in stem)[:50]
    unique_filename = f"{safe_stem}_{uuid.uuid4().hex[:8]}{ext}"
    target_path = target_folder / unique_filename
    
    # Save file to disk
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file to disk: {str(e)}")
    finally:
        file.file.close()
        
    filesize = target_path.stat().st_size
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    
    material_entry = {
        "id": f"mat_{uuid.uuid4().hex[:10]}",
        "title": title.strip(),
        "category": category.strip(),
        "chapter": chapter.strip(),
        "resource_type": chosen_type,
        "description": description.strip(),
        "tags": tag_list,
        "filename": unique_filename,
        "original_name": file.filename,
        "file_url": f"/uploads/{chosen_type}/{unique_filename}",
        "filesize": filesize,
        "filesize_formatted": format_file_size(filesize),
        "uploaded_at": datetime.utcnow().isoformat() + "Z"
    }
    
    materials = read_json(MATERIALS_FILE, [])
    materials.insert(0, material_entry)
    write_json(MATERIALS_FILE, materials)
    
    return {"status": "success", "message": "Resource successfully uploaded", "data": material_entry}

@app.delete("/api/materials/{material_id}")
async def delete_material(material_id: str):
    materials = read_json(MATERIALS_FILE, [])
    index = next((i for i, m in enumerate(materials) if m["id"] == material_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Material not found")
        
    deleted_item = materials.pop(index)
    write_json(MATERIALS_FILE, materials)
    
    # Delete file from filesystem if present
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
        
    # Return sanitized version for student browsing (hide answers/explanations)
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
async def get_admin_quizzes():
    quizzes = read_json(QUIZZES_FILE, [])
    return {"status": "success", "count": len(quizzes), "data": quizzes}

@app.get("/api/admin/quizzes/{quiz_id}")
async def get_admin_quiz_detail(quiz_id: str):
    quizzes = read_json(QUIZZES_FILE, [])
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"status": "success", "data": quiz}

@app.post("/api/quizzes")
async def create_quiz(payload: CreateQuizRequest):
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
        "created_at": datetime.utcnow().isoformat() + "Z",
        "questions": formatted_questions
    }
    
    quizzes = read_json(QUIZZES_FILE, [])
    quizzes.insert(0, quiz_entry)
    write_json(QUIZZES_FILE, quizzes)
    
    return {"status": "success", "message": "Quiz created successfully", "data": quiz_entry}

@app.delete("/api/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str):
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
    
    # Map questions for fast lookup
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
    
    # Store submission
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
async def get_submissions(quiz_id: Optional[str] = Query(None)):
    submissions = read_json(SUBMISSIONS_FILE, [])
    if quiz_id:
        submissions = [s for s in submissions if s.get("quiz_id") == quiz_id]
        
    submissions.sort(key=lambda s: s.get("submitted_at", ""), reverse=True)
    return {"status": "success", "count": len(submissions), "data": submissions}

@app.get("/api/submissions/{submission_id}")
async def get_submission_detail(submission_id: str):
    submissions = read_json(SUBMISSIONS_FILE, [])
    sub = next((s for s in submissions if s["id"] == submission_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission record not found")
        
    # Enrich with question texts from quiz
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
async def delete_submission(submission_id: str):
    submissions = read_json(SUBMISSIONS_FILE, [])
    index = next((i for i, s in enumerate(submissions) if s["id"] == submission_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    submissions.pop(index)
    write_json(SUBMISSIONS_FILE, submissions)
    return {"status": "success", "message": "Submission deleted"}

if __name__ == "__main__":
    import uvicorn
    print("Starting EduSphere Educational Platform on http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
