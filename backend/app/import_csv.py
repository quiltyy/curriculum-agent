import csv
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/curriculumdb"
engine = create_engine(DATABASE_URL, echo=True)

CSV_PATH = "test_data/test_courses.csv"  # relative to backend/


def parse_prerequisites(prereq_str):
    """
    Returns a list of groups for a course.
    Each group: {'type': 'AND'/'OR', 'courses': [course_codes]}
    """
    if not prereq_str:
        return []

    prereq_str = prereq_str.upper().strip()
    groups = []

    # Split on 'AND' first
    and_parts = [p.strip() for p in prereq_str.split(" AND ")]
    for part in and_parts:
        # If part contains OR
        if " OR " in part:
            or_courses = [c.strip() for c in part.split(" OR ")]
            groups.append({"type": "OR", "courses": or_courses})
        else:
            groups.append({"type": "AND", "courses": [part]})
    return groups


with engine.begin() as conn:
    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            program_name = row["program"].strip()
            course_code = row["course_code"].strip()
            course_name = row["course_name"].strip()
            credits = int(row["credits"])
            description = row["description"].strip()
            prereq_str = row.get("prerequisites", "")

            # --- Get or create program ---
            conn.execute(
                text("""
                    INSERT INTO programs (name) VALUES (:name)
                    ON CONFLICT (name) DO NOTHING;
                """),
                {"name": program_name},
            )
            program_id = conn.scalar(
                text("SELECT program_id FROM programs WHERE name=:name"),
                {"name": program_name},
            )

            # --- Get or create course ---
            conn.execute(
                text("""
                    INSERT INTO courses (program_id, course_code, course_name, credits, description)
                    VALUES (:program_id, :code, :name, :credits, :desc)
                    ON CONFLICT (program_id, course_code) DO NOTHING;
                """),
                {
                    "program_id": program_id,
                    "code": course_code,
                    "name": course_name,
                    "credits": credits,
                    "desc": description,
                },
            )
            course_id = conn.scalar(
                text("""
                    SELECT course_id FROM courses
                    WHERE program_id=:program_id AND course_code=:code
                """),
                {"program_id": program_id, "code": course_code},
            )

            # --- Handle prerequisites ---
            groups = parse_prerequisites(prereq_str)
            for g in groups:
                group_type = g["type"]
                prereq_codes = g["courses"]

                group_id = conn.scalar(
                    text("""
                        INSERT INTO prerequisite_groups (course_id, type)
                        VALUES (:course_id, :type)
                        RETURNING group_id
                    """),
                    {"course_id": course_id, "type": group_type},
                )

                for prereq_code in prereq_codes:
                    conn.execute(
                        text("""
                            INSERT INTO prerequisite_group_members (group_id, prereq_course_id)
                            SELECT :group_id, course_id FROM courses
                            WHERE course_code=:code
                            ON CONFLICT DO NOTHING;
                        """),
                        {"group_id": group_id, "code": prereq_code},
                    )

print("✅ CSV import completed successfully!")
