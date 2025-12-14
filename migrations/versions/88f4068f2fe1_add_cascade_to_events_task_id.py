"""add cascade to events.task_id

Revision ID: 88f4068f2fe1
Revises: 1275f0aa6432
Create Date: 2025-12-14 14:48:09.414813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88f4068f2fe1'
down_revision: Union[str, None] = '1275f0aa6432'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # удалить старый FK
    op.drop_constraint('fk_events_task_id_tasks', 'events', type_='foreignkey')
    # создать новый с CASCADE
    op.create_foreign_key(
        'fk_events_task_id_tasks',
        'events',
        'tasks',
        ['task_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('fk_events_task_id_tasks', 'events', type_='foreignkey')
    op.create_foreign_key(
        'fk_events_task_id_tasks',
        'events',
        'tasks',
        ['task_id'],
        ['id']
    )
