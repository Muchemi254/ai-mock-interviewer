# backend/common/models.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuestionType(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    CULTURAL = "cultural"

class Skill(BaseModel):
    name: str
    category: str
    level: Optional[SkillLevel] = None
    confidence: Optional[float] = Field(ge=0, le=1, default=None)
    years_experience: Optional[int] = None
    last_used: Optional[datetime] = None

class JobDescription(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    department: Optional[str] = None
    seniority_level: str
    location: Optional[str] = None
    salary_range: Optional[Dict[str, float]] = None
    raw_text: str
    parsed_requirements: List[str] = []
    skills: List[Skill] = []
    soft_skills: List[str] = []
    cultural_indicators: List[str] = []
    bias_flags: List[str] = []
    embedding_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class CVEntry(BaseModel):
    company: str
    role: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    achievements: List[str] = []
    technologies: List[str] = []
    team_size: Optional[int] = None
    reporting_level: Optional[str] = None

class CandidateCV(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    raw_text: str
    summary: Optional[str] = None
    entries: List[CVEntry] = []
    skills: List[Skill] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    languages: List[Dict[str, str]] = []
    total_experience_years: Optional[float] = None
    embedding_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# These can be moved to dialog-manager later, but useful for auth/session
class SessionState(BaseModel):
    session_id: str
    user_id: str
    job_id: str
    cv_id: str
    interview_type: str = "standard"
    total_time_seconds: int
    question_queue: List[Any] = [] # Using Any for now, will be Question model later
    current_index: int = 0
    time_allocations: Dict[str, int] = {} # question_id -> allocated_seconds
    followup_counts: Dict[str, int] = {} # question_id -> count
    time_remaining: int
    performance_metrics: Dict[str, Any] = {}
    audio_settings: Dict[str, Any] = {}
    interruptions: List[Dict[str, Any]] = []
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: str = "active" # active, paused, completed, terminated

# Simple User model for auth
class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
