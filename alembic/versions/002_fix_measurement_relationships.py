"""Fix measurement relationships and ensure all measurements have directories

Revision ID: 002_fix_measurement_relationships
Revises: 001_add_measurement_directory
Create Date: 2025-09-16 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_fix_measurements"
down_revision: Union[str, None] = "001_add_measurement_directory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraint to measurement_directory.path
    op.create_unique_constraint(
        "uq_measurement_directory_path", "measurement_directory", ["path"]
    )

    # Get connection to execute raw SQL
    connection = op.get_bind()

    # Create temporary table references
    measurements_table = table(
        "measurements",
        column("id", sa.Integer),
        column("experiment_id", sa.Integer),
        column("directory_id", sa.Integer),
    )

    measurement_directory_table = table(
        "measurement_directory",
        column("id", sa.Integer),
        column("path", sa.String),
        column("available", sa.Boolean),
        column("experiment_id", sa.Integer),
    )

    # Find measurements without directory_id (NULL values)
    measurements_without_dirs = connection.execute(
        sa.text(
            """
            SELECT id, experiment_id
            FROM measurements
            WHERE directory_id IS NULL
            """
        )
    ).fetchall()

    # For each measurement without a directory, create or find appropriate directory
    for measurement_id, experiment_id in measurements_without_dirs:
        directory_path = (
            f"/measurement_directory_for_experiment_{experiment_id}/"
        )

        # Check if directory already exists for this experiment
        existing_dir = connection.execute(
            sa.text(
                """
                SELECT id FROM measurement_directory
                WHERE path = :path
                """
            ),
            {"path": directory_path},
        ).fetchone()

        if existing_dir:
            # Directory exists, use it
            directory_id = existing_dir[0]
        else:
            # Create new directory
            result = connection.execute(
                measurement_directory_table.insert()
                .values(
                    path=directory_path,
                    available=True,
                    experiment_id=experiment_id,
                )
                .returning(measurement_directory_table.c.id)
            )
            directory_id = result.fetchone()[0]

        # Update measurement to use this directory
        connection.execute(
            sa.text(
                """
                UPDATE measurements
                SET directory_id = :directory_id
                WHERE id = :measurement_id
                """
            ),
            {"directory_id": directory_id, "measurement_id": measurement_id},
        )

    # Now remove experiment_id from measurements table since all measurements
    # can access experiment through directory.experiment

    # Drop foreign key constraint first
    op.drop_constraint(
        "measurements_experiment_id_fkey", "measurements", type_="foreignkey"
    )

    # Drop the experiment_id column
    op.drop_column("measurements", "experiment_id")


def downgrade() -> None:
    # Add experiment_id column back to measurements
    op.add_column(
        "measurements", sa.Column("experiment_id", sa.Integer(), nullable=True)
    )

    # Get connection to restore data
    connection = op.get_bind()

    # Populate experiment_id from directory relationship
    connection.execute(
        sa.text(
            """
            UPDATE measurements
            SET experiment_id = (
                SELECT md.experiment_id
                FROM measurement_directory md
                WHERE md.id = measurements.directory_id
            )
            """
        )
    )

    # Make experiment_id non-nullable
    op.alter_column("measurements", "experiment_id", nullable=False)

    # Restore foreign key constraint
    op.create_foreign_key(
        "measurements_experiment_id_fkey",
        "measurements",
        "experiments",
        ["experiment_id"],
        ["id"],
    )

    # Remove unique constraint from measurement_directory.path
    op.drop_constraint(
        "uq_measurement_directory_path",
        "measurement_directory",
        type_="unique",
    )
