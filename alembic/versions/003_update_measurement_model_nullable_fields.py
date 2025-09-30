"""update measurement model nullable fields

Revision ID: 003_update_measurement_model_nullable_fields
Revises: 002_fix_measurement_relationships
Create Date: 2025-09-30 12:58:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_nullable_fields"
down_revision: Union[str, None] = "002_fix_measurements"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get connection to check current schema
    connection = op.get_bind()

    # Check what columns exist in measurements table
    result = connection.execute(
        sa.text(
            """
        SELECT column_name, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'measurements'
        AND table_schema = 'public'
    """
        )
    )

    existing_columns = {row[0]: row[1] for row in result.fetchall()}

    # Only alter columns that exist and need changing
    if (
        "description" in existing_columns
        and existing_columns["description"] == "NO"
    ):
        op.alter_column(
            "measurements",
            "description",
            existing_type=sa.String(),
            nullable=True,
        )

    if (
        "number_of_files" in existing_columns
        and existing_columns["number_of_files"] == "NO"
    ):
        op.alter_column(
            "measurements",
            "number_of_files",
            existing_type=sa.Integer(),
            nullable=True,
        )

    if (
        "patient_reference" in existing_columns
        and existing_columns["patient_reference"] == "NO"
    ):
        op.alter_column(
            "measurements",
            "patient_reference",
            existing_type=sa.String(),
            nullable=True,
        )

    if (
        "shifter_id" in existing_columns
        and existing_columns["shifter_id"] == "NO"
    ):
        op.alter_column(
            "measurements",
            "shifter_id",
            existing_type=sa.Integer(),
            nullable=True,
        )

    # Remove directory column if it exists
    if "directory" in existing_columns:
        op.drop_column("measurements", "directory")


def downgrade() -> None:
    # Add directory column back
    op.add_column(
        "measurements", sa.Column("directory", sa.String(), nullable=False)
    )

    # Make shifter_id not nullable
    op.alter_column(
        "measurements",
        "shifter_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Make patient_reference not nullable
    op.alter_column(
        "measurements",
        "patient_reference",
        existing_type=sa.String(),
        nullable=False,
    )

    # Make number_of_files not nullable
    op.alter_column(
        "measurements",
        "number_of_files",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Make description not nullable
    op.alter_column(
        "measurements",
        "description",
        existing_type=sa.String(),
        nullable=False,
    )
