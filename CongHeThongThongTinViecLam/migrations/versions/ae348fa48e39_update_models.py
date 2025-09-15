"""update models

Revision ID: ae348fa48e39
Revises: 1c180c29b3d9
Create Date: 2025-09-15 11:54:13.743322

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ae348fa48e39'
down_revision = '1c180c29b3d9'
branch_labels = None
depends_on = None


def upgrade():
    # Nếu bảng additional_info đã drop rồi thì bỏ dòng này để tránh lỗi
    # op.drop_table('additional_info')

    with op.batch_alter_table('job_application', schema=None) as batch_op:
        # ✅ chỉ thêm cột mới 'design'
        batch_op.add_column(sa.Column('design', mysql.JSON(), nullable=True))
        # ✅ chỉ alter cv_data (không add lại)
        batch_op.alter_column(
            'cv_data',
            existing_type=mysql.JSON(),
            nullable=False
        )


def downgrade():
    with op.batch_alter_table('job_application', schema=None) as batch_op:
        batch_op.alter_column(
            'cv_data',
            existing_type=mysql.JSON(),
            nullable=True
        )
        batch_op.drop_column('design')

    # Nếu muốn phục hồi lại additional_info thì giữ nguyên
    op.create_table(
        'additional_info',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('title', mysql.VARCHAR(length=100), nullable=True),
        sa.Column('content', mysql.TEXT(), nullable=True),
        sa.Column('job_application_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        # sa.ForeignKeyConstraint(['job_application_id'], ['job_application.id'], name=op.f('additional_info_ibfk_1')),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
