from sqlalchemy import inspect, text

from src.db.base import Base, engine
from src.db.models import Students


def _add_missing_student_columns(connection) -> None:
    table = Students.__table__
    existing_columns = {
        column["name"] for column in inspect(connection).get_columns(table.name)
    }

    for name in ("username", "course"):
        if name not in existing_columns:
            column = table.c[name]
            preparer = connection.dialect.identifier_preparer
            connection.execute(
                text(
                    f"ALTER TABLE {preparer.format_table(table)} "
                    f"ADD COLUMN {preparer.quote(name)} "
                    f"{column.type.compile(dialect=connection.dialect)}"
                )
            )


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_add_missing_student_columns)