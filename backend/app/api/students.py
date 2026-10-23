"""
Student Directory & Detail Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.schemas.schemas import (
    PaginatedStudents, StudentDetail, StudentListItem, StudentRecordSummary
)
from database.connection import get_db
from database.models import AcademicRecordModel, StudentModel

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=PaginatedStudents)
def list_students(
    search: Optional[str] = Query(None, description="Search by student_id or school"),
    school: Optional[str] = Query(None, description="Filter by school: GP or MS"),
    course: Optional[str] = Query(None, description="Filter by course: MAT or POR"),
    risk_only: Optional[bool] = Query(None, description="Filter only students with academic risk"),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(StudentModel)

    if search:
        query = query.filter(
            (StudentModel.student_id.ilike(f"%{search}%")) |
            (StudentModel.school.ilike(f"%{search}%"))
        )

    if school:
        query = query.filter(StudentModel.school == school)

    if course:
        query = query.join(StudentModel.records).filter(AcademicRecordModel.course_code == course)

    if risk_only:
        query = query.join(StudentModel.records).filter(AcademicRecordModel.academic_risk == 1)

    # Distinct students
    query = query.distinct()
    total = query.count()

    total_pages = max(1, (total + page_size - 1) // page_size)
    offset = (page - 1) * page_size

    students = query.order_by(StudentModel.id.asc()).offset(offset).limit(page_size).all()

    items = []
    for s in students:
        courses = [r.course_code for r in s.records]
        final_grades = {r.course_code: r.g3 for r in s.records}
        has_risk = any(r.academic_risk == 1 for r in s.records)
        # Performance tier from worst or lowest grade
        lowest_grade = min([r.g3 for r in s.records]) if s.records else 0
        if lowest_grade < 10:
            tier = "Needs Support"
        elif lowest_grade < 14:
            tier = "Satisfactory"
        elif lowest_grade < 16:
            tier = "Good"
        else:
            tier = "Excellent"

        items.append(
            StudentListItem(
                id=s.id,
                student_id=s.student_id,
                school=s.school,
                sex=s.sex,
                age=s.age,
                address=s.address,
                courses=courses,
                final_grades=final_grades,
                is_at_risk=has_risk,
                performance_tier=tier
            )
        )

    return PaginatedStudents(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )


@router.get("/{student_id}", response_model=StudentDetail)
def get_student_detail(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    enrollments = [
        StudentRecordSummary(
            record_id=r.record_id,
            course_code=r.course_code,
            g1=r.g1,
            g2=r.g2,
            g3=r.g3,
            studytime=r.studytime,
            failures=r.failures,
            absences=r.absences,
            academic_risk=r.academic_risk,
            passing_status=r.passing_status,
            performance_tier=r.performance_tier
        )
        for r in student.records
    ]

    return StudentDetail(
        id=student.id,
        student_id=student.student_id,
        school=student.school,
        sex=student.sex,
        age=student.age,
        address=student.address,
        famsize=student.famsize,
        pstatus=student.pstatus,
        medu=student.medu,
        fedu=student.fedu,
        mjob=student.mjob,
        fjob=student.fjob,
        reason=student.reason,
        guardian=student.guardian,
        nursery=student.nursery,
        internet=student.internet,
        enrollments=enrollments
    )
