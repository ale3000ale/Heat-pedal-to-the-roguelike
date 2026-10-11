"""tabelle del negozio e inventario sponsor del pilota

Revision ID: a1c5e9b3d7f2
Revises: f6c0d4e8b3a9
Create Date: 2026-10-08 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1c5e9b3d7f2'
down_revision: Union[str, Sequence[str], None] = 'f6c0d4e8b3a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _pack_columns() -> list[sa.Column]:
    return [
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_path", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("modifiche_count", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("sponsor_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("filter_enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("filter_text", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    ]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())

    if "pack_template" not in tables:
        op.create_table(
            "pack_template",
            sa.Column("id", sa.Integer(), nullable=False),
            *_pack_columns(),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_pack_template_id"), "pack_template", ["id"], unique=False)

    if "shop_template" not in tables:
        op.create_table(
            "shop_template",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("name_key", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name_key", name="uq_shop_template_name_key"),
        )
        op.create_index(op.f("ix_shop_template_id"), "shop_template", ["id"], unique=False)

    if "shop_template_pack" not in tables:
        op.create_table(
            "shop_template_pack",
            sa.Column("shop_template_id", sa.Integer(), nullable=False),
            sa.Column("pack_template_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["shop_template_id"], ["shop_template.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["pack_template_id"], ["pack_template.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("shop_template_id", "pack_template_id"),
        )

    if "pack" not in tables:
        op.create_table(
            "pack",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("championship_id", sa.Integer(), nullable=False),
            *_pack_columns(),
            sa.ForeignKeyConstraint(["championship_id"], ["championship.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_pack_id"), "pack", ["id"], unique=False)
        op.create_index(op.f("ix_pack_championship_id"), "pack", ["championship_id"], unique=False)

    if "pack_purchase" not in tables:
        op.create_table(
            "pack_purchase",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("championship_id", sa.Integer(), nullable=False),
            sa.Column("pilot_id", sa.Integer(), nullable=True),
            sa.Column("pilot_name", sa.String(), nullable=False),
            sa.Column("pack_id", sa.Integer(), nullable=True),
            sa.Column("pack_name", sa.String(), nullable=False),
            sa.Column("currency", sa.String(), nullable=False),
            sa.Column("cost", sa.Integer(), nullable=False),
            sa.Column("cards_modifiche", sa.String(), nullable=True),
            sa.Column("cards_sponsor", sa.String(), nullable=True),
            sa.Column("purchased_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["championship_id"], ["championship.id"]),
            sa.ForeignKeyConstraint(["pilot_id"], ["pilot.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["pack_id"], ["pack.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_pack_purchase_id"), "pack_purchase", ["id"], unique=False)
        op.create_index(
            op.f("ix_pack_purchase_championship_id"), "pack_purchase", ["championship_id"], unique=False
        )

    pilot_columns = {c["name"] for c in sa.inspect(bind).get_columns("pilot")}
    if "sponsor_inventory_deck_id" in pilot_columns:
        return
    with op.batch_alter_table("pilot") as batch:
        batch.add_column(sa.Column("sponsor_inventory_deck_id", sa.Integer(), nullable=True))

    # Un mazzo sponsor vuoto per ogni pilota esistente.
    pilot_ids = [row[0] for row in bind.execute(sa.text("SELECT id FROM pilot"))]
    for pilot_id in pilot_ids:
        bind.execute(sa.text("INSERT INTO deck (cards, version) VALUES ('[]', 1)"))
        deck_id = bind.execute(sa.text("SELECT max(id) FROM deck")).scalar()
        bind.execute(
            sa.text("UPDATE pilot SET sponsor_inventory_deck_id = :d WHERE id = :p"),
            {"d": deck_id, "p": pilot_id},
        )

    with op.batch_alter_table("pilot") as batch:
        batch.alter_column("sponsor_inventory_deck_id", existing_type=sa.Integer(), nullable=False)
        batch.create_foreign_key(
            "fk_pilot_sponsor_inventory_deck_id", "deck", ["sponsor_inventory_deck_id"], ["id"]
        )
        batch.create_unique_constraint(
            "uq_pilot_sponsor_inventory_deck_id", ["sponsor_inventory_deck_id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("pilot") as batch:
        batch.drop_constraint("uq_pilot_sponsor_inventory_deck_id", type_="unique")
        batch.drop_constraint("fk_pilot_sponsor_inventory_deck_id", type_="foreignkey")
        batch.drop_column("sponsor_inventory_deck_id")

    op.drop_index(op.f("ix_pack_purchase_championship_id"), table_name="pack_purchase")
    op.drop_index(op.f("ix_pack_purchase_id"), table_name="pack_purchase")
    op.drop_table("pack_purchase")
    op.drop_index(op.f("ix_pack_championship_id"), table_name="pack")
    op.drop_index(op.f("ix_pack_id"), table_name="pack")
    op.drop_table("pack")
    op.drop_table("shop_template_pack")
    op.drop_index(op.f("ix_shop_template_id"), table_name="shop_template")
    op.drop_table("shop_template")
    op.drop_index(op.f("ix_pack_template_id"), table_name="pack_template")
    op.drop_table("pack_template")
