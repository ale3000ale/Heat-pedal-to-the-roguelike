"""unione delle due teste: oro per gara e negozio

Revision ID: b2d6f0a4c8e1
Revises: a1c5e9b3d7f2, c9f3a1b6d8e4
Create Date: 2026-10-08 22:10:00.000000

"""
from typing import Sequence, Union


revision: str = 'b2d6f0a4c8e1'
down_revision: Union[str, Sequence[str], None] = ('a1c5e9b3d7f2', 'c9f3a1b6d8e4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: nessuna modifica, unisce solo le due catene."""


def downgrade() -> None:
    """Downgrade schema: nessuna modifica."""
