# =============================================================================
# Purpose:
# This module defines the **task-related models** used in the Agent2Agent protocol.
#
# These models represent:
# - What a task looks like (`Task`)
# - The state of the task (`TaskStatus`, `TaskState`)
# - The messages exchanged during a task (`Message`, `TextPart`)
# - Parameters used when sending, querying, or canceling tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum                          # Used to create fixed-value constants (e.g. task states)
from uuid import uuid4                         # For generating unique identifiers
from pydantic import BaseModel, Field          # Pydantic for structured data validation
from typing import Any, Literal, List          # Type hints for flexibility and structure
from datetime import datetime                  # To store timestamps


# -----------------------------------------------------------------------------
# Message Part: Currently only text is supported
# -----------------------------------------------------------------------------

# Represents one part of a message, currently only plain text is allowed
class TextPart(BaseModel):
    type: Literal["text"] = "text"  # Fixed value field to identify this as a "text" type
    text: str                       # The actual text content (e.g., "What time is it?")

# Alias: For now, "Part" is the same as TextPart (used for easier refactoring in the future)
Part = TextPart


# -----------------------------------------------------------------------------
# Message: One entry in the task’s history
# -----------------------------------------------------------------------------

# A message in the context of a task, either from the user or the agent
class Message(BaseModel):
    role: Literal["user", "agent"]  # Who sent the message: "user" or "agent"
    parts: List[Part]               # Messages can have multiple parts (e.g., multiple lines of text)


# -----------------------------------------------------------------------------
# TaskStatus: Describes the state of a task at a given moment
# -----------------------------------------------------------------------------

class TaskStatus(BaseModel):
    state: str  # A string like "submitted", "working", etc. (defined more precisely in TaskState)
    
    # Automatically captures the time when the status is recorded
    timestamp: datetime = Field(default_factory=datetime.now)


# -----------------------------------------------------------------------------
# Task: The core unit of work in the Agent2Agent protocol
# -----------------------------------------------------------------------------

class Task(BaseModel):
    id: str                    # A unique identifier for this task (can be generated by client or agent)
    status: TaskStatus         # The current state of the task
    history: List[Message]     # Conversation history for the task (what the user said, how the agent replied)


# -----------------------------------------------------------------------------
# Parameter Models for API Requests
# -----------------------------------------------------------------------------

# Used to identify a task, e.g., when canceling or querying
class TaskIdParams(BaseModel):
    id: str                                # The task ID
    metadata: dict[str, Any] | None = None # Optional metadata for additional context (e.g., who submitted it)


# Extends TaskIdParams to include optional history length
# Useful when querying a task and controlling how much of the past you want back
class TaskQueryParams(TaskIdParams):
    historyLength: int | None = None       # Limit the number of messages returned in the task's history


# Parameters required to send a new task to an agent
class TaskSendParams(BaseModel):
    id: str                                # Task ID (usually generated client-side)
    
    # Session ID used to group related tasks (autogenerated if not provided)
    sessionId: str = Field(default_factory=lambda: uuid4().hex)

    message: Message                       # The message that initiates the task
    historyLength: int | None = None       # Optional history length to return
    metadata: dict[str, Any] | None = None # Optional extra info (e.g., user role, priority)


# -----------------------------------------------------------------------------
# TaskState: Enum for predefined task lifecycle states
# -----------------------------------------------------------------------------

# Enum gives you a controlled vocabulary for task states
class TaskState(str, Enum):
    SUBMITTED = "submitted"              # Task has been received
    WORKING = "working"                  # Task is in progress
    INPUT_REQUIRED = "input-required"    # Agent is waiting for more input
    COMPLETED = "completed"             # Task is done
    CANCELED = "canceled"               # Task was canceled by user or system
    FAILED = "failed"                   # Something went wrong
    UNKNOWN = "unknown"                 # Fallback for undefined or unrecognized states