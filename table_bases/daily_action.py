"""
    Scheme and Enums used for daily actions
"""
from enum import IntEnum
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from scripts.sqldata import engine

Base = declarative_base()


class DailyActionType(IntEnum):
    "Types of daily actions."
    IMAGE = 0x0001


# @dataclass
# class DailyAction:
#     "A daily action that can will be executed every day."
#     actiontype: DailyActionType
#     channel_id: int
#     guild_id: int
#     data: str  # search term or tags

# pylint: disable=too-few-public-methods
class DailyConfiguration(Base):
    """
        ORM class daily action
    """
    __tablename__ = "dailyactions"
    id = Column(Integer, primary_key=True)
    enabled_actions = Column(Integer, nullable=False)
    channel_id = Column(Integer, nullable=False)
    guild_id = Column(Integer, nullable=False)

    boorus = relationship(
        "BooruDaily", cascade="all, delete-orphan"
    )

class BooruDaily(Base):
    """
        ORM for image dailies
    """
    id = Column(Integer, ForeignKey("dailyactions.id"), primary_key=True)
    tags = Column(String, nullable=False)

DailyConfiguration.metadata.create_all(engine)
BooruDaily.metadata.create_all(engine)
