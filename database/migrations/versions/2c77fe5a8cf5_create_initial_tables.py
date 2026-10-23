"""create_initial_tables

Revision ID: 2c77fe5a8cf5
Revises: 
Create Date: 2026-10-23 13:27:58.512951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c77fe5a8cf5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. students table
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.String(length=32), nullable=False),
        sa.Column('school', sa.String(length=16), nullable=False),
        sa.Column('sex', sa.String(length=8), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=8), nullable=False),
        sa.Column('famsize', sa.String(length=8), nullable=False),
        sa.Column('pstatus', sa.String(length=8), nullable=False),
        sa.Column('medu', sa.Integer(), nullable=False),
        sa.Column('fedu', sa.Integer(), nullable=False),
        sa.Column('mjob', sa.String(length=32), nullable=False),
        sa.Column('fjob', sa.String(length=32), nullable=False),
        sa.Column('reason', sa.String(length=32), nullable=False),
        sa.Column('guardian', sa.String(length=16), nullable=False),
        sa.Column('nursery', sa.String(length=8), nullable=False),
        sa.Column('internet', sa.String(length=8), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id')
    )
    op.create_index(op.f('ix_students_student_id'), 'students', ['student_id'], unique=True)

    # 2. courses table
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('course_code', sa.String(length=16), nullable=False),
        sa.Column('course_name', sa.String(length=64), nullable=False),
        sa.Column('department', sa.String(length=128), nullable=True),
        sa.Column('credits', sa.Integer(), nullable=True),
        sa.Column('semester', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_code')
    )
    op.create_index(op.f('ix_courses_course_code'), 'courses', ['course_code'], unique=True)

    # 3. academic_records table
    op.create_table(
        'academic_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.String(length=32), nullable=False),
        sa.Column('student_id', sa.String(length=32), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('course_code', sa.String(length=16), nullable=False),
        sa.Column('traveltime', sa.Integer(), nullable=False),
        sa.Column('studytime', sa.Integer(), nullable=False),
        sa.Column('failures', sa.Integer(), nullable=False),
        sa.Column('schoolsup', sa.String(length=8), nullable=False),
        sa.Column('famsup', sa.String(length=8), nullable=False),
        sa.Column('paid', sa.String(length=8), nullable=False),
        sa.Column('activities', sa.String(length=8), nullable=False),
        sa.Column('higher', sa.String(length=8), nullable=False),
        sa.Column('romantic', sa.String(length=8), nullable=False),
        sa.Column('famrel', sa.Integer(), nullable=False),
        sa.Column('freetime', sa.Integer(), nullable=False),
        sa.Column('goout', sa.Integer(), nullable=False),
        sa.Column('dalc', sa.Integer(), nullable=False),
        sa.Column('walc', sa.Integer(), nullable=False),
        sa.Column('health', sa.Integer(), nullable=False),
        sa.Column('absences', sa.Integer(), nullable=False),
        sa.Column('g1', sa.Integer(), nullable=False),
        sa.Column('g2', sa.Integer(), nullable=False),
        sa.Column('g3', sa.Integer(), nullable=False),
        sa.Column('parent_edu_avg', sa.Float(), nullable=False),
        sa.Column('alcohol_index', sa.Float(), nullable=False),
        sa.Column('study_to_social_ratio', sa.Float(), nullable=False),
        sa.Column('grade_delta', sa.Integer(), nullable=False),
        sa.Column('academic_risk', sa.Integer(), nullable=False),
        sa.Column('passing_status', sa.Boolean(), nullable=False),
        sa.Column('performance_tier', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('record_id'),
        sa.UniqueConstraint('student_id', 'course_id', name='uq_student_course')
    )
    op.create_index(op.f('ix_academic_records_academic_risk'), 'academic_records', ['academic_risk'], unique=False)
    op.create_index(op.f('ix_academic_records_course_id'), 'academic_records', ['course_id'], unique=False)
    op.create_index(op.f('ix_academic_records_record_id'), 'academic_records', ['record_id'], unique=True)
    op.create_index(op.f('ix_academic_records_student_id'), 'academic_records', ['student_id'], unique=False)
    op.create_index('idx_student_course', 'academic_records', ['student_id', 'course_id'], unique=False)

    # 4. pipeline_executions table
    op.create_table(
        'pipeline_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_timestamp', sa.DateTime(), nullable=False),
        sa.Column('records_processed', sa.Integer(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. prediction_logs table
    op.create_table(
        'prediction_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('course', sa.String(length=16), nullable=False),
        sa.Column('features_json', sa.Text(), nullable=False),
        sa.Column('predicted_grade', sa.Float(), nullable=False),
        sa.Column('predicted_risk', sa.Integer(), nullable=False),
        sa.Column('risk_probability', sa.Float(), nullable=False),
        sa.Column('model_name', sa.String(length=64), nullable=False),
        sa.Column('model_version', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. data_imports table
    op.create_table(
        'data_imports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_name', sa.String(length=128), nullable=False),
        sa.Column('file_name', sa.String(length=128), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=128), nullable=False),
        sa.Column('imported_at', sa.DateTime(), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('data_imports')
    op.drop_table('prediction_logs')
    op.drop_table('pipeline_executions')
    op.drop_index('idx_student_course', table_name='academic_records')
    op.drop_index(op.f('ix_academic_records_student_id'), table_name='academic_records')
    op.drop_index(op.f('ix_academic_records_record_id'), table_name='academic_records')
    op.drop_index(op.f('ix_academic_records_course_id'), table_name='academic_records')
    op.drop_index(op.f('ix_academic_records_academic_risk'), table_name='academic_records')
    op.drop_table('academic_records')
    op.drop_index(op.f('ix_courses_course_code'), table_name='courses')
    op.drop_table('courses')
    op.drop_index(op.f('ix_students_student_id'), table_name='students')
    op.drop_table('students')
