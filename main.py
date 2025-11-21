import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="GEC Premium API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "GEC Backend Running"}


# ==================== CMS-like Public Endpoints ====================
class NewsOut(BaseModel):
    id: Optional[str] = None
    title: str
    date: str
    category: str
    content: Optional[str] = None
    image_url: Optional[str] = None
    cta_label: Optional[str] = None
    cta_href: Optional[str] = None
    pinned: bool = False


@app.get("/api/cms/news", response_model=List[NewsOut])
def list_news():
    # Seed announcement for Student Hub if not present
    ensure_seed_content()
    docs = get_documents("news", {}, limit=50)
    # Convert ObjectId to str id
    out = []
    for d in docs:
        d_copy = {
            "id": str(d.get("_id")),
            "title": d.get("title"),
            "date": d.get("date"),
            "category": d.get("category"),
            "content": d.get("content"),
            "image_url": d.get("image_url"),
            "cta_label": d.get("cta_label"),
            "cta_href": d.get("cta_href"),
            "pinned": d.get("pinned", False),
        }
        out.append(d_copy)
    # Sort pinned and by date desc (date as string YYYY-MM-DD or human)
    out.sort(key=lambda x: (not x.get("pinned", False), x.get("date", "")), reverse=True)
    return out


@app.get("/api/courses")
def list_courses():
    ensure_seed_content()
    courses = get_documents("course", {}, limit=100)
    for c in courses:
        c["id"] = str(c.get("_id"))
        c.pop("_id", None)
    return courses


@app.get("/api/faculty")
def list_faculty():
    ensure_seed_content()
    fac = get_documents("faculty", {}, limit=200)
    for f in fac:
        f["id"] = str(f.get("_id"))
        f.pop("_id", None)
    return fac


# ==================== Student Hub Auth (Demo) ====================
class LoginRequest(BaseModel):
    roll: Optional[str] = None
    dob: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


@app.post("/api/student/login")
def student_login(payload: LoginRequest):
    ensure_seed_content()
    # Very simple mock auth against seeded student
    students = get_documents("student", {"roll": payload.roll} if payload.roll else {"email": payload.email})
    if not students:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    student = students[0]
    if payload.roll and payload.dob:
        if student.get("dob") != payload.dob:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    elif payload.email and payload.password:
        # For demo only: password stored as plain text sample
        if student.get("password_hash") != payload.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        raise HTTPException(status_code=400, detail="Provide roll+dob or email+password")

    return {
        "token": "demo-token",
        "student": {
            "id": str(student.get("_id")),
            "name": student.get("name"),
            "roll": student.get("roll"),
            "program": student.get("program"),
            "semester": student.get("semester"),
            "department": student.get("department"),
        },
    }


@app.get("/api/student/{student_id}/attendance")
def get_attendance(student_id: str):
    ensure_seed_content()
    recs = get_documents("attendance", {"student_id": student_id})
    for r in recs:
        r["id"] = str(r.get("_id"))
        r.pop("_id", None)
    return recs


@app.get("/api/student/{student_id}/results")
def get_results(student_id: str):
    ensure_seed_content()
    recs = get_documents("result", {"student_id": student_id})
    for r in recs:
        r["id"] = str(r.get("_id"))
        r.pop("_id", None)
    return recs


@app.get("/api/student/{student_id}/fees")
def get_fees(student_id: str):
    ensure_seed_content()
    recs = get_documents("fee", {"student_id": student_id})
    for r in recs:
        r["id"] = str(r.get("_id"))
        r.pop("_id", None)
    return recs


@app.get("/api/student/{student_id}/timetable")
def get_timetable(student_id: str):
    ensure_seed_content()
    # Return program/semester specific timetable for demo student
    student = get_documents("student", {"_id": {"$exists": True}}, limit=1)[0]
    tt = get_documents("timetable", {"program": student.get("program"), "semester": student.get("semester")}, limit=1)
    if not tt:
        return {"week": []}
    doc = tt[0]
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return doc


# ==================== Seed Data Helper ====================

def ensure_seed_content():
    """Seed minimal content needed for the demo if collections are empty."""
    try:
        # Seed news with Student Hub announcement
        news = get_documents("news", {"title": {"$regex": "Student Hub Launched", "$options": "i"}}, limit=1)
        if not news:
            create_document(
                "news",
                {
                    "title": "Student Hub Launched – View Attendance, Results & Academic Records Online",
                    "date": "Nov 20, 2025",
                    "category": "Student Services",
                    "content": "Log in to access attendance, results, fees, assignments, and more.",
                    "cta_label": "Go to Student Hub (Login Required)",
                    "cta_href": "/student/login",
                    "pinned": True,
                },
            )
        # Seed a few courses
        if not get_documents("course", {}, limit=1):
            for c in [
                {"name": "B.Tech Computer Science & Engineering", "level": "UG", "branch": "CSE", "duration": "4 Years", "intake": 180},
                {"name": "B.Tech Electronics & Communication Engineering", "level": "UG", "branch": "ECE", "duration": "4 Years", "intake": 120},
                {"name": "MBA Master of Business Administration", "level": "PG", "branch": "MBA", "duration": "2 Years", "intake": 60},
            ]:
                create_document("course", c)
        # Seed faculty sample
        if not get_documents("faculty", {}, limit=1):
            for f in [
                {"name": "Dr. A. Kumar", "designation": "Professor & HOD", "department": "CSE", "specialization": "AI & ML", "email": "a.kumar@gec.edu.in"},
                {"name": "Dr. S. Mishra", "designation": "Associate Professor", "department": "ECE", "specialization": "VLSI", "email": "s.mishra@gec.edu.in"},
            ]:
                create_document("faculty", f)
        # Seed demo student and related academic docs
        if not get_documents("student", {}, limit=1):
            sid = create_document(
                "student",
                {
                    "roll": "GEC2021CSE001",
                    "name": "Rohit Sharma",
                    "email": "rohit.sharma@gec.edu.in",
                    "dob": "2003-05-18",
                    "department": "CSE",
                    "program": "B.Tech",
                    "semester": 5,
                    "password_hash": "demo123",
                },
            )
            # Attendance
            for sub, pct in [("Data Structures", 88.5), ("Operating Systems", 92.0), ("DBMS", 84.0)]:
                create_document("attendance", {"student_id": sid, "subject": sub, "percentage": pct, "month": "Nov 2025"})
            # Results
            create_document(
                "result",
                {
                    "student_id": sid,
                    "semester": 4,
                    "sgpa": 8.72,
                    "cgpa": 8.35,
                    "subjects": [
                        {"name": "Algorithms", "grade": "A"},
                        {"name": "Computer Networks", "grade": "A-"},
                        {"name": "Microprocessors", "grade": "B+"},
                    ],
                },
            )
            # Fees
            create_document(
                "fee",
                {"student_id": sid, "semester": 5, "status": "Due", "amount_due": 35000.0},
            )
            # Timetable
            create_document(
                "timetable",
                {
                    "program": "B.Tech",
                    "semester": 5,
                    "week": [
                        {"day": "Mon", "slots": ["DS", "OS", "DBMS", "--", "AI Lab"]},
                        {"day": "Tue", "slots": ["CN", "DBMS", "OS", "--", "Project"]},
                        {"day": "Wed", "slots": ["AI", "DS", "Elective", "--", "Sports"]},
                    ],
                },
            )
    except Exception as e:
        # Fail silently in seeding to avoid startup crash
        print("Seed error:", str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
