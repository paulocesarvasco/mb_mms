from typing import Optional
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class MovingAverage(Base):
    __tablename__ = "moving_averages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pair: Mapped[str] = mapped_column(String(10), index=True)
    timestamp: Mapped[int] = mapped_column(BigInteger, index=True)
    mms_20: Mapped[Optional[float]]
    mms_50: Mapped[Optional[float]]
    mms_200: Mapped[Optional[float]]
