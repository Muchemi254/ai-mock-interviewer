# backend/common/database_models.py
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
import enum

# Base declarative class
Base = declarative_base()


# -----------------------------
# ENUMS
# -----------------------------
class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionType(str, enum.Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    CULTURAL = "cultural"


# -----------------------------
# USER
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# -----------------------------
# JOB DESCRIPTION
# -----------------------------
class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    department = Column(String, nullable=True)
    seniority_level = Column(String, nullable=False)
    location = Column(String, nullable=True)
    salary_range = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_requirements = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    cultural_indicators = Column(JSON, default=list)
    bias_flags = Column(JSON, default=list)
    embedding_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    level = Column(Enum(SkillLevel), nullable=True)
    confidence = Column(Float, nullable=True)
    years_experience = Column(Integer, nullable=True)
    last_used = Column(DateTime, nullable=True)

    job = relationship("JobDescription", back_populates="skills")


# -----------------------------
# CANDIDATE CV
# -----------------------------
class CandidateCV(Base):
    __tablename__ = "candidate_cvs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    certifications = Column(JSON, default=list)
    education = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    total_experience_years = Column(Float, nullable=True)
    embedding_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    entries = relationship("CVEntry", back_populates="cv", cascade="all, delete-orphan")
    skills = relationship("CVSkill", back_populates="cv", cascade="all, delete-orphan")


class CVEntry(Base):
    __tablename__ = "cv_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("candidate_cvs.id", ondelete="CASCADE"), nullable=False)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    achievements = Column(JSON, default=list)
    technologies = Column(JSON, default=list)
    team_size = Column(Integer, nullable=True)
    reporting_level = Column(String, nullable=True)

    cv = relationship("CandidateCV", back_populates="entries")


class CVSkill(Base):
    __tablename__ = "cv_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("candidate_cvs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    level = Column(Enum(SkillLevel), nullable=True)
    confidence = Column(Float, nullable=True)
    years_experience = Column(Integer, nullable=True)
    last_used = Column(DateTime, nullable=True)

    cv = relationship("CandidateCV", back_populates="skills")


# -----------------------------
# SESSION STATE
# -----------------------------
class SessionState(Base):
    __tablename__ = "session_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=True)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("candidate_cvs.id", ondelete="CASCADE"), nullable=True)
    interview_type = Column(String, default="standard", nullable=False)
    total_time_seconds = Column(Integer, nullable=False)
    question_queue = Column(JSON, default=list)
    current_index = Column(Integer, default=0)
    time_allocations = Column(JSON, default=dict)
    followup_counts = Column(JSON, default=dict)
    time_remaining = Column(Integer, nullable=False)
    performance_metrics = Column(JSON, default=dict)
    audio_settings = Column(JSON, default=dict)
    interruptions = Column(JSON, default=list)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="active", nullable=False)

    user = relationship("User")
    job = relationship("JobDescription")
    cv = relationship("CandidateCV")
