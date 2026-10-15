"""Motion & Animation Flow Agent (قسم التحريك والتدفق البصري).
Transforms static scene frames into dynamic animated video with options 2 & 3:
- Real animated camera & particle flow (Option 2)
- Synchronized Arabic subtitles with full tashkeel & floating overlays (Option 3)
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseAgent
from .animation_engine import AnimationEngine

class MotionAnimatorAgent(BaseAgent):
    """Specialist agent responsible for animating static frames, camera flow, subtitles, and video composition."""

    def __init__(self):
        super().__init__(
            name="Kenji Sato",
            role="Lead Motion Director & Camera Flow Engineer"
        )
        self.engine = AnimationEngine(base_dir=self.base_dir)

    def run(
        self,
        image_path: Path,
        audio_path: Path,
        bgm_path: Optional[Path] = None,
        output_video_path: Optional[Path] = None,
        topic_title: str = "حِكَايَاتُ العَجَائِب",
        script_text: str = ""
    ) -> Dict[str, Any]:
        """Execute animation flow pipeline with options 2 & 3."""
        if not bgm_path:
            bgm_path = self.scenes_dir / "kids_gentle_bgm.wav"

        if not output_video_path:
            output_video_path = self.output_dir / "studio_renders" / "animated_flow_output.mp4"

        rendered_path = self.engine.render_animated_episode(
            scene_image_path=image_path,
            audio_path=audio_path,
            bgm_path=bgm_path,
            topic_title=topic_title,
            script_text=script_text,
            output_video_path=output_video_path
        )

        return {
            "status": "success",
            "video_path": str(rendered_path),
            "resolution": "1080x1920",
            "fps": 30,
            "flow_style": "Option 2 (Kinetic Motion & Floating Stars) + Option 3 (Tashkeel Subtitles & Pedagogical Badges)"
        }

