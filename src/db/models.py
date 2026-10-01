from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, index=True
    )
    group_name: Mapped[str] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} group={self.group_name}>"