"""add prerequisite_groups tables

Revision ID: 580050a57662
Revises: 8f880d17d2af
Create Date: 2025-10-01 19:28:53.734934

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "580050a57662"
down_revision: Union[str, Sequence[str], None] = "8f880d17d2af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "prerequisite_groups",
        sa.Column("group_id", sa.Integer, primary_key=True),
        sa.Column(
            "course_id", sa.Integer, sa.ForeignKey("courses.course_id"), nullable=False
        ),
        sa.Column("type", sa.String, nullable=False),
    )
    op.create_table(
        "prerequisite_group_members",
        sa.Column("group_member_id", sa.Integer, primary_key=True),
        sa.Column(
            "group_id",
            sa.Integer,
            sa.ForeignKey("prerequisite_groups.group_id"),
            nullable=False,
        ),
        sa.Column(
            "prereq_course_id",
            sa.Integer,
            sa.ForeignKey("courses.course_id"),
            nullable=False,
        ),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
