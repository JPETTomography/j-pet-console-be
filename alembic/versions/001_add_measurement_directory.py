"""Add MeasurementDirectory table and migrate data

Revision ID: 001_add_measurement_directory
Revises: 
Create Date: 2025-08-26 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_add_measurement_directory"
down_revision: Union[str, None] = "000_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create measurement_directory table
    op.create_table(
        "measurement_directory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_measurement_directory_id"),
        "measurement_directory",
        ["id"],
        unique=False,
    )

    # Create temporary table references for data migration
    measurement_table = table(
        "measurements",
        column("id", sa.Integer),
        column("directory", sa.String),
        column("experiment_id", sa.Integer),
    )

    measurement_directory_table = table(
        "measurement_directory",
        column("id", sa.Integer),
        column("path", sa.String),
        column("available", sa.Boolean),
        column("experiment_id", sa.Integer),
    )

    # Get connection to execute raw SQL
    connection = op.get_bind()

    # Migrate existing measurement directories to new table
    # First, get all unique directory paths with their experiment_id
    result = connection.execute(
        sa.text(
            """
            SELECT DISTINCT directory, experiment_id 
            FROM measurements 
            WHERE directory IS NOT NULL 
            AND directory != ''
        """
        )
    )

    # Insert directories into measurement_directory table
    for row in result:
        directory_path, experiment_id = row
        connection.execute(
            measurement_directory_table.insert().values(
                path=directory_path,
                available=True,
                experiment_id=experiment_id,
            )
        )

    # Add directory_id column to measurements table
    op.add_column(
        "measurements", sa.Column("directory_id", sa.Integer(), nullable=True)
    )

    # Update measurements to reference the new measurement_directory entries
    connection.execute(
        sa.text(
            """
            UPDATE measurements 
            SET directory_id = (
                SELECT md.id 
                FROM measurement_directory md 
                WHERE md.path = measurements.directory 
                AND md.experiment_id = measurements.experiment_id
            )
            WHERE directory IS NOT NULL 
            AND directory != ''
        """
        )
    )

    # Make directory_id non-nullable and add foreign key
    op.alter_column("measurements", "directory_id", nullable=False)
    op.create_foreign_key(
        "fk_measurements_directory_id",
        "measurements",
        "measurement_directory",
        ["directory_id"],
        ["id"],
    )

    # Drop the old directory column
    op.drop_column("measurements", "directory")


def downgrade() -> None:
    # Add back the directory column
    op.add_column(
        "measurements", sa.Column("directory", sa.String(), nullable=True)
    )

    # Get connection to execute raw SQL
    connection = op.get_bind()

    # Restore directory values from measurement_directory table
    connection.execute(
        sa.text(
            """
            UPDATE measurements 
            SET directory = (
                SELECT md.path 
                FROM measurement_directory md 
                WHERE md.id = measurements.directory_id
            )
        """
        )
    )

    # Make directory column non-nullable
    op.alter_column("measurements", "directory", nullable=False)

    # Drop foreign key and directory_id column
    op.drop_constraint(
        "fk_measurements_directory_id", "measurements", type_="foreignkey"
    )
    op.drop_column("measurements", "directory_id")

    # Drop measurement_directory table
    op.drop_index(
        op.f("ix_measurement_directory_id"), table_name="measurement_directory"
    )
    op.drop_table("measurement_directory")
