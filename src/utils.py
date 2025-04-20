"""
Utility Functions for the Whisper Client
Version: 1.3
Timestamp: 2025-04-20 16:46 CET

This module provides utility functions for the Whisper Client.
It includes functions for server status checking, project status updates,
task history tracking, and displaying messages to the user.
"""

import json
import os
import socket
from datetime import datetime

import config
from src import logger
from src.logging import log_debug, log_error, log_info


def check_server_status(host=config.WS_HOST, port=config.WS_PORT):
    """Checks if the WhisperLive Server is running"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        log_debug(logger, "Error checking server status: %s", e)
        return False


def update_project_status(description=None, changes=None, status=None, files=None):
    """Updates the project status and task history"""
    try:
        # Update projects file
        projects_file = "projects.json"
        if os.path.exists(projects_file):
            with open(projects_file, "r", encoding="utf-8") as f:
                projects = json.load(f)

            # Find current project
            project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            for project in projects["projects"]:
                if project["path"] == project_path:
                    # Update status
                    if status:
                        project["status"] = status

                    # Add task
                    if description and changes:
                        task = {
                            "description": description,
                            "status": "completed",
                            "details": changes[0]["description"] if changes else None,
                        }
                        project["current_tasks"].insert(0, task)  # Newest task first

                    # Update timestamp
                    current_time = datetime.now().isoformat()
                    project["last_updated"] = current_time
                    projects["meta"]["last_updated"] = current_time
                    break

            # Save
            with open(projects_file, "w", encoding="utf-8") as f:
                json.dump(projects, f, indent=2, ensure_ascii=False)

    except Exception as e:
        log_error(logger, "⚠️ Error updating project status: %s", e)

    # Update task history
    if description and changes:
        update_task_history(description, changes, "completed", files)


def update_task_history(description, changes, status="completed", files=None):
    """Updates the task history"""
    history_file = "task_history.json"

    try:
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"tasks": []}

        # Add new task
        task = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "changes": changes,
            "status": status,
        }
        if files:
            task["files"] = files

        history["tasks"].insert(0, task)  # Newest task first

        # Save
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    except Exception as e:
        log_error(logger, "⚠️ Error updating task history: %s", e)


def show_startup_message():
    """Shows the startup message"""
    startup_msg = f"""
=== Whisper Client ===
🔥 Client started!
⌨️  Press {config.HOTKEY_TOGGLE_RECORDING} to start/stop recording
⚡ Press {config.HOTKEY_EXIT} to exit
--------------------------------------------------"""

    # Only send to logger
    for line in startup_msg.split("\n"):
        if line.strip():
            log_info(logger, line)


def show_server_error():
    """Shows error message when server is not reachable"""
    error_msg = """
⚠️ WhisperLive Server is not reachable!

Please start the server with one of the following commands:

1. Directly from the source code:
   cd path/to/whisperlive
   python server.py

2. Or as a Docker Container:
   docker run -p 9090:9090 whisperlive

Then restart this client."""

    # Only send to logger
    for line in error_msg.split("\n"):
        if line.strip():
            log_error(logger, line)
