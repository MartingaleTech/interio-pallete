"""Convert date strings to DateTime and remove denormalized fields

Revision ID: e229523c5b5e
Revises: 35b04cfa8df9
Create Date: 2025-11-05 05:49:36.081929

"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e229523c5b5e'
down_revision: Union[str, Sequence[str], None] = '35b04cfa8df9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def parse_datetime(date_str):
    """Parse string date to datetime object with timezone awareness.
    
    Handles common date formats:
    - ISO 8601: "2025-01-15T10:30:00Z" or "2025-01-15T10:30:00"
    - Date only: "2025-01-15"
    - Datetime: "2025-01-15 10:30:00"
    """
    if date_str is None:
        return None
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    
    return None


def upgrade() -> None:
    """Upgrade schema with data conversion for SQLite compatibility."""
    bind = op.get_bind()
    
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_date_dt', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('end_date_dt', sa.DateTime(), nullable=True))
    
    rows = bind.execute(sa.text("SELECT id, start_date, end_date FROM projects")).fetchall()
    for row in rows:
        start_dt = parse_datetime(row.start_date) if row.start_date else None
        end_dt = parse_datetime(row.end_date) if row.end_date else None
        bind.execute(
            sa.text("UPDATE projects SET start_date_dt=:sd, end_date_dt=:ed WHERE id=:id"),
            {"sd": start_dt, "ed": end_dt, "id": row.id}
        )
    
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('start_date')
        batch_op.drop_column('end_date')
        batch_op.alter_column('start_date_dt', new_column_name='start_date', 
                            existing_type=sa.DateTime(), nullable=False)
        batch_op.alter_column('end_date_dt', new_column_name='end_date',
                            existing_type=sa.DateTime(), nullable=True)
        batch_op.drop_column('client_name')
    
    with op.batch_alter_table('calendar_events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_time_dt', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('end_time_dt', sa.DateTime(), nullable=True))
    
    rows = bind.execute(sa.text("SELECT id, start_time, end_time FROM calendar_events")).fetchall()
    for row in rows:
        start_dt = parse_datetime(row.start_time) if row.start_time else None
        end_dt = parse_datetime(row.end_time) if row.end_time else None
        bind.execute(
            sa.text("UPDATE calendar_events SET start_time_dt=:st, end_time_dt=:et WHERE id=:id"),
            {"st": start_dt, "et": end_dt, "id": row.id}
        )
    
    with op.batch_alter_table('calendar_events', schema=None) as batch_op:
        batch_op.drop_column('start_time')
        batch_op.drop_column('end_time')
        batch_op.alter_column('start_time_dt', new_column_name='start_time',
                            existing_type=sa.DateTime(), nullable=False)
        batch_op.alter_column('end_time_dt', new_column_name='end_time',
                            existing_type=sa.DateTime(), nullable=False)
    
    with op.batch_alter_table('project_designs', schema=None) as batch_op:
        batch_op.drop_column('uploaded_by')
    
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=False,
                                      server_default=sa.text("datetime('now', '+30 days')")))


def downgrade() -> None:
    """Downgrade schema (data loss for denormalized fields)."""
    bind = op.get_bind()
    
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.drop_column('expires_at')
    
    with op.batch_alter_table('project_designs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uploaded_by', sa.VARCHAR(), nullable=True))
    
    with op.batch_alter_table('calendar_events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_time_str', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('end_time_str', sa.VARCHAR(), nullable=True))
    
    rows = bind.execute(sa.text("SELECT id, start_time, end_time FROM calendar_events")).fetchall()
    for row in rows:
        start_str = row.start_time.isoformat() if row.start_time else None
        end_str = row.end_time.isoformat() if row.end_time else None
        bind.execute(
            sa.text("UPDATE calendar_events SET start_time_str=:st, end_time_str=:et WHERE id=:id"),
            {"st": start_str, "et": end_str, "id": row.id}
        )
    
    with op.batch_alter_table('calendar_events', schema=None) as batch_op:
        batch_op.drop_column('start_time')
        batch_op.drop_column('end_time')
        batch_op.alter_column('start_time_str', new_column_name='start_time',
                            existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('end_time_str', new_column_name='end_time',
                            existing_type=sa.VARCHAR(), nullable=False)
    
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_date_str', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('end_date_str', sa.VARCHAR(), nullable=True))
    
    rows = bind.execute(sa.text("SELECT id, start_date, end_date FROM projects")).fetchall()
    for row in rows:
        start_str = row.start_date.isoformat() if row.start_date else None
        end_str = row.end_date.isoformat() if row.end_date else None
        bind.execute(
            sa.text("UPDATE projects SET start_date_str=:sd, end_date_str=:ed WHERE id=:id"),
            {"sd": start_str, "ed": end_str, "id": row.id}
        )
    
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('start_date')
        batch_op.drop_column('end_date')
        batch_op.alter_column('start_date_str', new_column_name='start_date',
                            existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('end_date_str', new_column_name='end_date',
                            existing_type=sa.VARCHAR(), nullable=True)
        batch_op.add_column(sa.Column('client_name', sa.VARCHAR(), nullable=True))
