"""Database integration wrapper for backend services."""

try:
    from packages.integrations.database import engine, SessionLocal, init_db
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "The integrations package is required: 'packages.integrations.database' not found."
    ) from e
