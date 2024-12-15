from fastapi import FastAPI
from pydantic import BaseModel
import time
from threading import Thread
import threading

# FastAPI app instance
app = FastAPI()

# Timer state
timer_state = {
    "work_duration": 25 * 60,  # Default 25 minutes for work
    "break_duration": 5 * 60,  # Default 5 minutes for break
    "remaining_time": 25 * 60,  # Initially set to work_duration
    "timer_running": False,
    "timer_type": "work",  # "work" or "break"
    "timer_thread": None
}

# Timer Model for Input
class TimerSettings(BaseModel):
    work_duration: int  # In seconds
    break_duration: int  # In seconds

# Function to run the timer (works in a separate thread)
def run_timer():
    while timer_state["timer_running"]:
        time.sleep(1)
        timer_state["remaining_time"] -= 1
        
        # Check if the timer has completed
        if timer_state["remaining_time"] <= 0:
            if timer_state["timer_type"] == "work":
                # Switch to break after work time is done
                timer_state["timer_type"] = "break"
                timer_state["remaining_time"] = timer_state["break_duration"]
            else:
                # Switch to work after break time is done
                timer_state["timer_type"] = "work"
                timer_state["remaining_time"] = timer_state["work_duration"]

# Start the timer with provided work and break durations
@app.post("/start/")
def start_timer(settings: TimerSettings):
    if timer_state["timer_running"]:
        return {"message": "Timer is already running."}

    # Update work and break durations
    timer_state["work_duration"] = settings.work_duration
    timer_state["break_duration"] = settings.break_duration
    timer_state["remaining_time"] = settings.work_duration  # Start with work duration
    timer_state["timer_running"] = True
    timer_state["timer_type"] = "work"

    # Run the timer in a separate thread
    timer_state["timer_thread"] = Thread(target=run_timer, daemon=True)
    timer_state["timer_thread"].start()

    return {"message": "Timer started!", "work_duration": settings.work_duration, "break_duration": settings.break_duration}

# Stop the timer
@app.post("/stop/")
def stop_timer():
    if not timer_state["timer_running"]:
        return {"message": "Timer is not running."}
    
    # Stop the timer
    timer_state["timer_running"] = False
    return {"message": "Timer stopped."}

# Reset the timer
@app.post("/reset/")
def reset_timer():
    timer_state["remaining_time"] = timer_state["work_duration"]
    timer_state["timer_type"] = "work"
    return {"message": "Timer reset.", "remaining_time": timer_state["remaining_time"]}

# Get the current state of the timer
@app.get("/status/")
def get_timer_status():
    remaining_minutes = timer_state["remaining_time"] // 60
    remaining_seconds = timer_state["remaining_time"] % 60
    return {
        "timer_running": timer_state["timer_running"],
        "timer_type": timer_state["timer_type"],
        "remaining_time": f"{remaining_minutes:02}:{remaining_seconds:02}"
    }
