from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base


class Students(Base):
    __tablename__ = "Students"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, index=True
    )
    group_name: Mapped[str] = mapped_column(String(50), nullable=True)

    uni_name: Mapped[str] = mapped_column(String(20), nullable=False)

    subgroup_number: Mapped[int | None] = mapped_column(Integer,nullable=True)

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} group={self.group_name}>"