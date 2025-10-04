# backend/app/api/graph.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import networkx as nx

from backend.app.db import models, database

router = APIRouter()


@router.get("/{program_id}")
def get_program_graph(program_id: int, db: Session = Depends(database.get_db)):
    """
    Returns a prerequisite graph for a given program in Cytoscape.js JSON format.
    Nodes use course_code as ID, edges link course_code -> course_code.
    """

    # 1. Get all courses for this program
    courses = (
        db.query(models.Course).filter(models.Course.program_id == program_id).all()
    )
    if not courses:
        raise HTTPException(
            status_code=404, detail="Program not found or has no courses"
        )

    # 2. Build directed graph
    G = nx.DiGraph()

    # Nodes: use course_code as id, course_name as label
    for course in courses:
        G.add_node(course.course_code, label=course.course_name)

    # Edges: prereq.course_code -> course.course_code
    prereqs = (
        db.query(models.Prerequisite)
        .join(models.Course, models.Prerequisite.course_id == models.Course.course_id)
        .filter(models.Course.program_id == program_id)
        .all()
    )
    for prereq in prereqs:
        source = db.query(models.Course).get(prereq.prereq_course_id).course_code
        target = db.query(models.Course).get(prereq.course_id).course_code
        if source and target:
            G.add_edge(source, target)

    # 3. Convert to Cytoscape.js format
    nodes = [
        {"data": {"id": node, "label": G.nodes[node]["label"]}} for node in G.nodes
    ]
    edges = [{"data": {"source": u, "target": v}} for u, v in G.edges]

    return {"nodes": nodes, "edges": edges}
