"""
Database Schemas for Gandhi Engineering College (GEC)

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

# Public content schemas
class Course(BaseModel):
    name: str = Field(..., description="Program name, e.g., B.Tech CSE")
    level: str = Field(..., description="UG or PG")
    branch: Optional[str] = Field(None, description="Discipline/Branch")
    duration: str = Field(..., description="e.g., 4 Years")
    intake: int = Field(..., ge=0, description="Sanctioned intake")
    about: Optional[str] = None
    eligibility: Optional[str] = None
    outcomes: Optional[List[str]] = None
    syllabus_pdf: Optional[str] = None

class Faculty(BaseModel):
    name: str
    designation: str
    department: str
    specialization: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None

class News(BaseModel):
    title: str
    date: str
    category: str
    content: Optional[str] = None
    image_url: Optional[str] = None
    cta_label: Optional[str] = None
    cta_href: Optional[str] = None
    pinned: bool = False

# Student and academic schemas
class Student(BaseModel):
    roll: str
    name: str
    email: str
    dob: date
    department: str
    program: str
    semester: int
    phone: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    address: Optional[str] = None
    password_hash: Optional[str] = None

class Attendance(BaseModel):
    student_id: str
    subject: str
    percentage: float
    month: str

class Result(BaseModel):
    student_id: str
    semester: int
    sgpa: float
    cgpa: float
    subjects: List[dict]

class Fee(BaseModel):
    student_id: str
    semester: int
    status: str
    amount_due: float
    last_payment_date: Optional[str] = None
    receipt_url: Optional[str] = None

class Assignment(BaseModel):
    title: str
    course: str
    due_date: str
    description: Optional[str] = None

class Submission(BaseModel):
    assignment_id: str
    student_id: str
    submitted_at: Optional[str] = None
    file_url: Optional[str] = None

class Timetable(BaseModel):
    program: str
    semester: int
    week: List[dict]

class Notice(BaseModel):
    audience: str
    title: str
    body: Optional[str] = None
    date: str
    pinned: bool = False
