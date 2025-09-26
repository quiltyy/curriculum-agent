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

    # Insert prerequisites
    prereqs = [
        ("CS102", "CS101"),
        ("CS201", "CS102"),
        ("CS202", "CS101"),
        ("CS301", "CS201"),
        ("CS302", "CS201"),
        ("CS401", "CS202"),
        ("CS402", "CS302"),
    ]

    for course, prereq in prereqs:
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

print("✅ Seed data inserted successfully!")
