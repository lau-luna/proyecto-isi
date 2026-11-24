"""add user role check

Only allow the roles of the User subclasses in user.role.
Written by hand: Alembic autogenerate does not detect CHECK constraints.

Revision ID: 65fd0c52d9c9
Revises: f2751dd0c94f
Create Date: 2026-11-20 22:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '65fd0c52d9c9'
down_revision = 'f2751dd0c94f'
branch_labels = None
depends_on = None


def upgrade():
    # batch_alter_table: SQLite cannot add a constraint to an existing table,
    # so Alembic rebuilds the table with the constraint included.
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_check_constraint(
            'ck_user_role',
            "role IN ('regular_user', 'moderator', 'administrator')",
        )


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('ck_user_role', type_='check')
