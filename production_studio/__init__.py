"""Kids YouTube Production Studio - Multi-Agent Architecture.
A Pixar-grade AI production house for children's educational content in Modern Standard Arabic.
"""

from .base import BaseAgent
from .scriptwriter import ScriptwriterAgent
from .art_director import ArtDirectorAgent
from .motion_animator import MotionAnimatorAgent
from .sound_director import SoundDirectorAgent
from .copywriter import CopywriterAgent
from .qa_director import QADirectorAgent
from .orchestrator import StudioOrchestrator

__all__ = [
    "BaseAgent",
    "ScriptwriterAgent",
    "ArtDirectorAgent",
    "MotionAnimatorAgent",
    "SoundDirectorAgent",
    "CopywriterAgent",
    "QADirectorAgent",
    "StudioOrchestrator",
]
