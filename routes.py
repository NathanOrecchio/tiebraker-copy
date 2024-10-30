from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import db

from models import EventList

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Get all Events
@router.get("/", response_description="List all events", response_model=EventList, response_model_by_alias=False, response_class=HTMLResponse)
async def find_events(request : Request):

    summer_events =  ["662a899da5509d7343eca861", "662a8c82926b2476e08dedef", "662a8da0926b2476e08dedf0"]
    event_data = await db.get_event_data(event_list=summer_events)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "data": event_data
    })