"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-03-23 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Enable pgvector
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # 2. Enums
    sa.Enum('CANDIDATE', 'EMPLOYER', 'ADMIN', name='userrole').create(op.get_bind())
    sa.Enum('OPEN', 'CLOSED', 'DRAFT', name='jobstatus').create(op.get_bind())
    sa.Enum('REQUIRED', 'PREFERRED', name='importancelevel').create(op.get_bind())
    sa.Enum('HIRED', 'REJECTED', 'NO_RESPONSE', name='hireoutcomeenum').create(op.get_bind())

    # 3. Tables
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('CANDIDATE', 'EMPLOYER', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('candidate_profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('headline', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('years_experience', sa.Float(), nullable=True),
        sa.Column('raw_resume_text', sa.Text(), nullable=True),
        sa.Column('parsed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    op.create_table('employers',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('size', sa.String(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    op.create_table('skills_taxonomy',
        sa.Column('uri', sa.String(), nullable=False),
        sa.Column('preferred_label', sa.String(), nullable=False),
        sa.Column('alt_labels', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('uri')
    )
    op.create_index(op.f('ix_skills_taxonomy_preferred_label'), 'skills_taxonomy', ['preferred_label'], unique=False)

    op.create_table('job_postings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employer_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('remote_ok', sa.Boolean(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'CLOSED', 'DRAFT', name='jobstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['employer_id'], ['employers.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_postings_employer_id'), 'job_postings', ['employer_id'], unique=False)
    op.create_index(op.f('ix_job_postings_id'), 'job_postings', ['id'], unique=False)

    op.create_table('candidate_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(), nullable=False),
        sa.Column('esco_uri', sa.String(), nullable=True),
        sa.Column('proficiency_level', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidate_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidate_skills_candidate_id'), 'candidate_skills', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_candidate_skills_esco_uri'), 'candidate_skills', ['esco_uri'], unique=False)
    op.create_index(op.f('ix_candidate_skills_id'), 'candidate_skills', ['id'], unique=False)

    op.create_table('job_required_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(), nullable=False),
        sa.Column('esco_uri', sa.String(), nullable=True),
        sa.Column('importance', sa.Enum('REQUIRED', 'PREFERRED', name='importancelevel'), nullable=True),
        sa.Column('min_proficiency', sa.Integer(), nullable=True),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_required_skills_esco_uri'), 'job_required_skills', ['esco_uri'], unique=False)
    op.create_index(op.f('ix_job_required_skills_id'), 'job_required_skills', ['id'], unique=False)
    op.create_index(op.f('ix_job_required_skills_job_id'), 'job_required_skills', ['job_id'], unique=False)

    op.create_table('skill_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('gap_skills', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidate_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('hire_outcomes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('outcome', sa.Enum('HIRED', 'REJECTED', 'NO_RESPONSE', name='hireoutcomeenum'), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidate_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('learning_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(), nullable=False),
        sa.Column('course_title', sa.String(), nullable=True),
        sa.Column('course_url', sa.String(), nullable=True),
        sa.Column('platform', sa.String(), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidate_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # Drop in reverse order
    op.drop_table('learning_recommendations')
    op.drop_table('hire_outcomes')
    op.drop_table('skill_matches')
    op.drop_index(op.f('ix_job_required_skills_job_id'), table_name='job_required_skills')
    op.drop_index(op.f('ix_job_required_skills_id'), table_name='job_required_skills')
    op.drop_index(op.f('ix_job_required_skills_esco_uri'), table_name='job_required_skills')
    op.drop_table('job_required_skills')
    op.drop_index(op.f('ix_candidate_skills_id'), table_name='candidate_skills')
    op.drop_index(op.f('ix_candidate_skills_esco_uri'), table_name='candidate_skills')
    op.drop_index(op.f('ix_candidate_skills_candidate_id'), table_name='candidate_skills')
    op.drop_table('candidate_skills')
    op.drop_index(op.f('ix_job_postings_id'), table_name='job_postings')
    op.drop_index(op.f('ix_job_postings_employer_id'), table_name='job_postings')
    op.drop_table('job_postings')
    op.drop_index(op.f('ix_skills_taxonomy_preferred_label'), table_name='skills_taxonomy')
    op.drop_table('skills_taxonomy')
    op.drop_table('employers')
    op.drop_table('candidate_profiles')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    sa.Enum(name='hireoutcomeenum').drop(op.get_bind())
    sa.Enum(name='importancelevel').drop(op.get_bind())
    sa.Enum(name='jobstatus').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())

    op.execute('DROP EXTENSION IF EXISTS vector')
