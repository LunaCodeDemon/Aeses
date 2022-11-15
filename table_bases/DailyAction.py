from enum import Enum
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DailyActionType(Enum):
    "Types of daily actions."
    IMAGE = "safebooru"


# @dataclass
# class DailyAction:
#     "A daily action that can will be executed every day."
#     actiontype: DailyActionType
#     channel_id: int
#     guild_id: int
#     data: str  # search term or tags

class DailyAction(Base):
    """
        ORM class daily action
    """
    __tablename__ = "dailyactions"
    id = Column(Integer, primary_key=True)
    actiontype = Column(String)
    channel_id = Column(Integer)
    guild_id = Column(Integer)
    data = Column(String)
    