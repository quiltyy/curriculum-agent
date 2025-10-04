from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# === Users ===
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    progress = relationship("StudentProgress", back_populates="user")


# === Programs ===
class Program(Base):
    __tablename__ = "programs"

    program_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    courses = relationship("Course", back_populates="program")


# === Courses ===
class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(
        Integer, ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False
    )
    course_code = Column(String(20), nullable=False)
    course_name = Column(String(255), nullable=False)
    credits = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    program = relationship("Program", back_populates="courses")

    # Relationships to prerequisites
    prerequisites = relationship(
        "Prerequisite", foreign_keys="Prerequisite.course_id", back_populates="course"
    )
    required_for = relationship(
        "Prerequisite",
        foreign_keys="Prerequisite.prereq_course_id",
        back_populates="prerequisite",
    )

    prereq_groups = relationship("PrerequisiteGroup", back_populates="course")

    progress = relationship("StudentProgress", back_populates="course")

    __table_args__ = (
        UniqueConstraint("program_id", "course_code", name="uq_program_course_code"),
    )


# === Simple prerequisites (legacy 1-to-1) ===
class Prerequisite(Base):
    __tablename__ = "prerequisites"

    prereq_id = Column(Integer, primary_key=True)
    course_id = Column(
        Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    prereq_course_id = Column(
        Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )

    course = relationship(
        "Course", foreign_keys=[course_id], back_populates="prerequisites"
    )
    prerequisite = relationship(
        "Course", foreign_keys=[prereq_course_id], back_populates="required_for"
    )


# === Complex prerequisite groups ===
class PrerequisiteGroup(Base):
    __tablename__ = "prerequisite_groups"

    group_id = Column(Integer, primary_key=True)
    course_id = Column(
        Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    type = Column(String(10), nullable=False)  # "AND" or "OR"

    course = relationship("Course", back_populates="prereq_groups")
    members = relationship("PrerequisiteGroupMember", back_populates="group")


class PrerequisiteGroupMember(Base):
    __tablename__ = "prerequisite_group_members"

    group_member_id = Column(Integer, primary_key=True)
    group_id = Column(
        Integer,
        ForeignKey("prerequisite_groups.group_id", ondelete="CASCADE"),
        nullable=False,
    )
    prereq_course_id = Column(
        Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )

    group = relationship("PrerequisiteGroup", back_populates="members")
    prereq_course = relationship("Course")


# === Student progress ===
class StudentProgress(Base):
    __tablename__ = "student_progress"

    progress_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    course_id = Column(
        Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String(20), nullable=False)
    updated_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="progress")
    course = relationship("Course", back_populates="progress")

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)
