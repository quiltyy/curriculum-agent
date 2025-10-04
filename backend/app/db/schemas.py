# backend/app/schemas.py
from pydantic import BaseModel, ConfigDict
from enum import Enum


# ============================================================
# Enums
# ============================================================


class UserRole(str, Enum):
    admin = "admin"
    advisor = "advisor"
    student = "student"


# ============================================================
# Auth Schemas
# ============================================================


class RegisterIn(BaseModel):
    email: str
    password: str
    role: UserRole


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str


class MeOut(BaseModel):
    user_id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class RefreshIn(BaseModel):
    refresh_token: str


# ============================================================
# Program & Course Schemas
# ============================================================


class ProgramOut(BaseModel):
    program_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CourseOut(BaseModel):
    course_id: int
    program_id: int
    course_code: str
    course_name: str
    credits: int | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Graph Schemas
# ============================================================


class GraphNode(BaseModel):
    id: int
    label: str


class GraphEdge(BaseModel):
    source: int
    target: int


class GraphOut(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ============================================================
# Student Progress Schemas
# ============================================================


class StudentProgressOut(BaseModel):
    progress_id: int
    user_id: int
    course_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
