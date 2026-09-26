# EduSphere — Complete Educational Web Platform

EduSphere is a full-stack, production-grade educational platform built with **Python (FastAPI)**, **thread-safe JSON data storage**, and a modern, responsive **Tailwind CSS + Vanilla JavaScript frontend**.

---

## 🌟 Key Features

### 1. 🎓 Student Hub (`/`)
- **Resource Explorer & Filters**:
  - Filter materials by **Subject / Category** (Physics, Computer Science, Biology, Mathematics, Astronomy, etc.).
  - Filter by **Resource Type**:
    - 📄 **Documents & Notes** (PDF, TXT, DOCX)
    - 🎥 **Video Lectures** (MP4, WebM)
    - 🎧 **Audio & Podcasts** (MP3, WAV)
    - 🖼️ **Diagrams & Photos** (PNG, JPG)
    - 📊 **Slide Decks & Presentations** (PDF, PPTX)
  - **Live Search**: Instant keyword search matching titles, chapters, descriptions, and tags.
- **Built-in Rich Media Viewers**:
  - **Document Viewer**: Text reader with zoomable font sizes (A- / A+) and embedded PDF viewer.
  - **Video Player**: HTML5 video playback with custom speed controls (0.75x, 1x, 1.25x, 1.5x, 2.0x).
  - **Sticky Audio Bar**: Custom audio player with equalizer animation, progress bar scrubber, rewind/forward 5s, and volume slider.
  - **Diagram & Image Gallery**: High-definition viewer with zoom in/out controls and pan support.
  - **Slide Deck Viewer**: Presentation viewer optimized for landscape lecture slides.
- **Direct Revision Downloads**: Download button on every material card.
- **Interactive Quiz Taker**:
  - Browse active quizzes by subject.
  - Timed assessments with dynamic question progress bars.
  - Instant score calculation and submission stored directly to `data/submissions.json`.
  - Comprehensive post-quiz review highlighting student selections, correct answer keys, and teacher explanations.

---

### 2. 👨‍🏫 Teacher / Admin Portal (`/admin`)
- **👑 Super Admin & Privacy Controller (Anubhav)**:
  - Master Super Admin account (`anubhavrbl06@gmail.com` or `admin`).
  - **Upload Access Control**: Only authorized users can upload resources. Unauthorized requests receive `401 Unauthorized` / `403 Forbidden`.
  - **Live Permission Switch**: Toggle any teacher's upload permissions (`Allowed` vs `Blocked`) in real time.
  - **⚡ One-Time Upload Passes**: Generate instant single-use passcodes (e.g. `PASS-PHYS72`) for guest lecturers or teachers. Once they upload 1 resource, their access automatically expires and cannot be reused!
  - **Account Types**: Assign teachers either **Permanent Upload Rights** or **One-Time Upload Rights**.
- **Educational Resource Uploader**:
  - Drag-and-drop or browse file picker.
  - Automatic category/type detection from file extension with optional manual override.
  - Rich metadata attachments: Title, Subject, Chapter/Unit, Description, and Comma-Separated Tags.
  - Automatically organizes physical files into categorized folders (`uploads/documents/`, `uploads/videos/`, `uploads/audio/`, `uploads/images/`, `uploads/slides/`).
- **Resource Management**:
  - Searchable inventory of uploaded files.
  - Quick action buttons to preview in browser, download, or delete from disk and database.
- **Interactive Quiz Builder**:
  - Form to define Quiz Title, Subject, Chapter, Time Limit (minutes), and Instructions.
  - Dynamic Question Creator with points, multiple choices, answer keys, and explanations.
- **Quiz Submissions & Grading Analytics**:
  - Real-time submissions table with student name, score, total points, percentage badge, and timestamp.
  - **Answer Sheet Inspector**: Modal that displays the student's complete test paper with question-by-question breakdown, student choices, correct answer keys, and explanations.

---

## 📁 Project Structure

```
educational_platform/
├── app.py                     # FastAPI application & all REST API endpoints
├── requirements.txt           # Python package dependencies
├── seed_data.py               # Database and sample educational media generator
├── test_platform.py           # Automated test suite for all endpoints
├── README.md                  # Documentation and setup instructions
│
├── data/                      # JSON Database storage
│   ├── materials.json         # Educational resources metadata
│   ├── quizzes.json           # Interactive quizzes and question keys
│   └── submissions.json       # Student submissions, scores, and answer papers
│
├── uploads/                   # Categorized physical file storage
│   ├── documents/             # PDFs, TXT study notes
│   ├── videos/                # MP4 video recordings
│   ├── audio/                 # MP3 podcast/lecture audio
│   ├── images/                # PNG/JPG scientific diagrams
│   └── slides/                # PDF/PPTX presentation slide decks
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom glassmorphism, scrollbars, animations
│   └── js/
│       ├── app.js             # Student hub UI logic, viewers, and quiz engine
│       └── admin.js           # Admin portal UI logic, uploader, and quiz builder
│
└── templates/
    ├── index.html             # Student portal HTML
    └── admin.html             # Teacher/Admin portal HTML
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13, 3.14 supported).

### 2. Install Dependencies
In the project root directory (`d:\educational_platform`), run:
```bash
pip install -r requirements.txt
```

*(Packages installed: `fastapi`, `uvicorn`, `python-multipart`, `pydantic`, `pillow`, `reportlab`)*

### 3. Generate Seed Data (Already Prepared)
Sample media files, quizzes, and initial student records are already generated in `data/` and `uploads/`. If you ever want to reset the database to sample seed data, run:
```bash
python seed_data.py
```

### 4. Run the Server
Start the application with Uvicorn:
```bash
python app.py
```
Or with Uvicorn directly:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🌐 Accessing the Platform

| Portal / Page | URL | Description |
|---|---|---|
| **Student Portal** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Browse materials, use viewers, take interactive quizzes |
| **Teacher / Admin Portal** | [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) | Upload resources, build quizzes, inspect submissions |
| **Interactive API Docs (Swagger)** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Complete OpenAPI interactive documentation |
| **Alternative API Docs (ReDoc)** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Clean ReDoc API specifications |

---

## 🧪 Running Automated Tests

Run the built-in test suite to verify all endpoints, file upload/download, and quiz grading logic:
```bash
python test_platform.py
```

All 7 tests verify:
- `GET /` and `GET /admin` templates load correctly.
- `GET /api/stats` and `GET /api/categories` return aggregated stats.
- `GET /api/materials` filters by category and resource type.
- `POST /api/materials` multipart file upload, storage, and `DELETE /api/materials/{id}` cleanup.
- `GET /api/quizzes` hides correct answers from student endpoints to avoid cheating.
- `POST /api/quizzes/{id}/submit` calculates scores, percentages, and stores submissions.
- `GET /api/submissions` retrieves grading records for teacher inspection.
