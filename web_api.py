from fastapi import FastAPI, BackgroundTasks, HTTPException
import time
from colony import Colony
from game import (
    generate_resources,
    build_structure,
    trigger_random_event,
    AVAILABLE_EVENT_CLASSES,
    resolve_major_event,
    BUILDING_CLASSES,
)
from research import RESEARCH_PROJECTS

app = FastAPI()

colony = Colony()
last_update = time.time()
current_major_event = None


def update_resources():
    """Generate resources based on real time elapsed."""
    global last_update
    now = time.time()
    elapsed = now - last_update
    if elapsed > 0:
        generate_resources(colony, elapsed)
    last_update = now


@app.get("/state")
def get_state(background_tasks: BackgroundTasks):
    """Return current colony state."""
    background_tasks.add_task(update_resources)
    return colony.to_dict()


@app.post("/build")
def build(data: dict, background_tasks: BackgroundTasks):
    """Construct a building by name."""
    background_tasks.add_task(update_resources)
    name = data.get("building")
    if not name:
        raise HTTPException(status_code=400, detail="Missing building name")
    cls = BUILDING_CLASSES.get(name)
    if not cls:
        raise HTTPException(status_code=400, detail="Unknown building")
    success = build_structure(colony, cls)
    return {"success": success, "state": colony.to_dict()}


@app.post("/upgrade")
def upgrade(data: dict, background_tasks: BackgroundTasks):
    """Upgrade a building by index."""
    background_tasks.add_task(update_resources)
    if "index" not in data:
        raise HTTPException(status_code=400, detail="Missing index")
    index = int(data["index"])
    success = colony.upgrade_building(index)
    return {"success": success, "state": colony.to_dict()}


@app.post("/research")
def research(data: dict, background_tasks: BackgroundTasks):
    """Research a technology project."""
    background_tasks.add_task(update_resources)
    project_id = data.get("project_id")
    if not project_id:
        raise HTTPException(status_code=400, detail="Missing project_id")
    if project_id not in RESEARCH_PROJECTS:
        raise HTTPException(status_code=400, detail="Invalid project_id")
    success = colony.research_project(project_id)
    return {"success": success, "state": colony.to_dict()}


@app.post("/event")
def event(data: dict | None = None, background_tasks: BackgroundTasks = None):
    """Trigger or resolve events."""
    background_tasks.add_task(update_resources)
    global current_major_event
    choice = None
    if data:
        choice = data.get("choice")

    if current_major_event and choice:
        resolve_major_event(colony, current_major_event, choice)
        current_major_event = None
        return {"state": colony.to_dict()}

    if current_major_event:
        return {
            "event": {
                "name": current_major_event.name,
                "description": current_major_event.description,
                "choices": current_major_event.choices,
            }
        }

    event_instance = trigger_random_event(colony, AVAILABLE_EVENT_CLASSES)
    if event_instance and event_instance.is_major:
        current_major_event = event_instance
        return {
            "event": {
                "name": event_instance.name,
                "description": event_instance.description,
                "choices": event_instance.choices,
            }
        }
    return {"state": colony.to_dict()}
