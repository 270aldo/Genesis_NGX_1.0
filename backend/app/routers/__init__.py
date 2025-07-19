from app.routers import (
    auth,
    agents,
    chat,
    stream,
    feedback,
    visualization,
    wearables,
    nutrition_vision,
    collaboration,
)

__all__ = [
    "auth",
    "agents",
    "chat",
    "stream",
    "feedback",
    "visualization",
    "wearables",
    "nutrition_vision",
    "collaboration",
]
from .a2a_standard import router
