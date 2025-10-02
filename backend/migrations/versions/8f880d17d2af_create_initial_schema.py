"""create initial schema

Revision ID: 8f880d17d2af
Revises:
Create Date: 2025-09-25 20:01:59.122152
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8f880d17d2af"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # === USERS ===
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(150), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # === PROGRAMS ===
    op.create_table(
        "programs",
        sa.Column("program_id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # === COURSES ===
    op.create_table(
        "courses",
        sa.Column("course_id", sa.Integer, primary_key=True),
        sa.Column(
            "program_id",
            sa.Integer,
            sa.ForeignKey("programs.program_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("course_code", sa.String(20), nullable=False),
        sa.Column("course_name", sa.String(255), nullable=False),
        sa.Column("credits", sa.Integer),
        sa.Column("description", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("program_id", "course_code", name="uq_program_course_code"),
    )

    # === SIMPLE PREREQUISITES ===
    op.create_table(
        "prerequisites",
        sa.Column("prereq_id", sa.Integer, primary_key=True),
        sa.Column(
            "course_id",
            sa.Integer,
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "prereq_course_id",
            sa.Integer,
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("course_id", "prereq_course_id", name="uq_course_prereq"),
    )

    # === COMPLEX PREREQUISITES (Groups) ===
    op.create_table(
        "prerequisite_groups",
        sa.Column("group_id", sa.Integer, primary_key=True),
        sa.Column(
            "course_id",
            sa.Integer,
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(10), nullable=False),  # 'AND' or 'OR'
    )

    op.create_table(
        "prerequisite_group_members",
        sa.Column("group_member_id", sa.Integer, primary_key=True),
        sa.Column(
            "group_id",
            sa.Integer,
            sa.ForeignKey("prerequisite_groups.group_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "prereq_course_id",
            sa.Integer,
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("group_id", "prereq_course_id", name="uq_group_prereq"),
    )

    # === STUDENT PROGRESS ===
    op.create_table(
        "student_progress",
        sa.Column("progress_id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Integer,
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

    # === INDEXES ===
    op.create_index(
        "idx_courses_program_code", "courses", ["program_id", "course_code"]
    )
    op.create_index("idx_prereq_course", "prerequisites", ["course_id"])
    op.create_index("idx_prereq_prereq", "prerequisites", ["prereq_course_id"])
    op.create_index("idx_student_progress_user", "student_progress", ["user_id"])
    op.create_index("idx_student_progress_course", "student_progress", ["course_id"])


def downgrade():
    # Drop in reverse dependency order
    op.drop_index("idx_student_progress_course", table_name="student_progress")
    op.drop_index("idx_student_progress_user", table_name="student_progress")
    op.drop_table("student_progress")

    op.drop_table("prerequisite_group_members")
    op.drop_table("prerequisite_groups")

    op.drop_index("idx_prereq_prereq", table_name="prerequisites")
    op.drop_index("idx_prereq_course", table_name="prerequisites")
    op.drop_table("prerequisites")

    op.drop_index("idx_courses_program_code", table_name="courses")
    op.drop_table("courses")

    op.drop_table("programs")
    op.drop_table("users")
