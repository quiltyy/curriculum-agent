from sqlalchemy import create_engine, text

# Use the same credentials as your docker-compose.yml
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/curriculumdb"

engine = create_engine(DATABASE_URL, echo=True)

with engine.begin() as conn:
    # Insert a demo program (ignore if it already exists)
    conn.execute(
        text("""
        INSERT INTO programs (name) 
        VALUES ('BS Computer Science')
        ON CONFLICT (name) DO NOTHING;
    """)
    )

    # Get the program_id
    program_id = conn.scalar(
        text("SELECT program_id FROM programs WHERE name='BS Computer Science'")
    )

    # Insert demo courses
    courses = [
        ("CS101", "Intro to CS", 4, "Basics of computing"),
        ("CS102", "Data Structures", 4, "Core data structures"),
        ("CS201", "Algorithms", 4, "Algorithm design and analysis"),
        ("CS202", "Computer Architecture", 4, "CPU, memory, and hardware"),
        ("CS301", "Operating Systems", 4, "Processes, threads, concurrency"),
        ("CS302", "Databases", 4, "Relational databases & SQL"),
        ("CS401", "Networks", 4, "Networking fundamentals"),
        ("CS402", "Machine Learning", 4, "Intro to ML techniques"),
        ("BIO252", "Cell Biology", 4, "Intro to cells"),
        ("BIO253", "Genetics", 4, "Genetics basics"),
        ("TCHEM212", "Organic Chemistry", 4, "Organic molecules"),
        ("BIO300", "Advanced Biology", 4, "Advanced topics in biology"),
    ]

    for code, name, credits, desc in courses:
        conn.execute(
            text("""
            INSERT INTO courses (program_id, course_code, course_name, credits, description)
            VALUES (:program_id, :code, :name, :credits, :desc)
            ON CONFLICT (program_id, course_code) DO NOTHING;
        """),
            {
                "program_id": program_id,
                "code": code,
                "name": name,
                "credits": credits,
                "desc": desc,
            },
        )

    # Insert simple prerequisites
    simple_prereqs = [
        ("CS102", "CS101"),
        ("CS201", "CS102"),
        ("CS202", "CS101"),
        ("CS301", "CS201"),
        ("CS302", "CS201"),
        ("CS401", "CS202"),
        ("CS402", "CS302"),
    ]

    for course, prereq in simple_prereqs:
        conn.execute(
            text("""
            INSERT INTO prerequisites (course_id, prereq_course_id)
            SELECT c1.course_id, c2.course_id
            FROM courses c1, courses c2
            WHERE c1.course_code = :course AND c2.course_code = :prereq
            ON CONFLICT DO NOTHING;
        """),
            {"course": course, "prereq": prereq},
        )

    # Insert complex prerequisites for BIO300: (BIO252 OR BIO253) AND TCHEM212
    course_id = conn.scalar(
        text("SELECT course_id FROM courses WHERE course_code='BIO300'")
    )

    # Group 1: OR -> BIO252 or BIO253
    group1_id = conn.scalar(
        text("""
            INSERT INTO prerequisite_groups (course_id, type)
            VALUES (:course_id, 'OR')
            RETURNING group_id
        """),
        {"course_id": course_id},
    )

    for prereq_code in ["BIO252", "BIO253"]:
        conn.execute(
            text("""
                INSERT INTO prerequisite_group_members (group_id, prereq_course_id)
                SELECT :group_id, course_id
                FROM courses
                WHERE course_code = :prereq
                ON CONFLICT DO NOTHING;
            """),
            {"group_id": group1_id, "prereq": prereq_code},
        )

    # Group 2: AND -> TCHEM212
    group2_id = conn.scalar(
        text("""
            INSERT INTO prerequisite_groups (course_id, type)
            VALUES (:course_id, 'AND')
            RETURNING group_id
        """),
        {"course_id": course_id},
    )

    conn.execute(
        text("""
            INSERT INTO prerequisite_group_members (group_id, prereq_course_id)
            SELECT :group_id, course_id
            FROM courses
            WHERE course_code = 'TCHEM212'
            ON CONFLICT DO NOTHING;
        """),
        {"group_id": group2_id},
    )

print("✅ Seed data inserted successfully!")
