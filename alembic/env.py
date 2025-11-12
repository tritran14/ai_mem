from logging.config import fileConfig
from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy.engine import Connection

from src.ai_mem.server import model  # ensure all models imported

config = context.config
fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata  # this enables autogeneration


def do_run_migrations(connection: Connection) -> None:
    """Actual migration runner (used for online mode)."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
