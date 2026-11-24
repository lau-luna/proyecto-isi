"""Merge user role and question category migrations

Revision ID: d603aad21a85
Revises: 65fd0c52d9c9, a627d319d4ee
Create Date: 2026-11-24 16:40:05.831315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd603aad21a85'
down_revision = ('65fd0c52d9c9', 'a627d319d4ee')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
