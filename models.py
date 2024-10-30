from typing import Annotated, Optional, List
from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]

class Roster(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    name : str = Field(...)
    red_cards : int = Field(...)
    yellow_cards : int = Field(...)


class RosterList(BaseModel):
    rosters : List[Roster]


class AgeDivision(BaseModel):
    year : int = Field(...)
    rosters : RosterList


class AgeDivisionList(BaseModel):
    age_divisions : List[AgeDivision]


class FutsalEvent(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    roster_id : PyObjectId = Field(...)
    user : str = Field(...)
    action : str = Field(...)


class FutsalEventList(BaseModel):
    futsal_events : List[FutsalEvent]


class Event(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    name : str = Field(...)
    boys_roster : AgeDivisionList
    girls_rosters : AgeDivisionList


class EventList(BaseModel):
    events : List[Event]