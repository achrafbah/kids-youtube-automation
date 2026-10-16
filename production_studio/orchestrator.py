"""Studio Production Orchestrator (المشرف العام على استوديو الإنتاج).
Coordinates the multi-agent production pipeline from concept to published episode.
"""

import datetime
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .scriptwriter import ScriptwriterAgent
from .art_director import ArtDirectorAgent
from .motion_animator import MotionAnimatorAgent
from .sound_director import SoundDirectorAgent
from .copywriter import CopywriterAgent
from .qa_director import QADirectorAgent

from youtube_uploader import upload_video

class StudioOrchestrator:
    """Production studio pipeline orchestrator connecting all specialized agents."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.output_dir = self.base_dir / "output"
        self.data_dir = self.base_dir / "data"
        self.history_file = self.data_dir / "topics_history.json"

        # Initialize the Department Agents
        self.scriptwriter = ScriptwriterAgent()
        self.art_director = ArtDirectorAgent()
        self.sound_director = SoundDirectorAgent()
        self.motion_animator = MotionAnimatorAgent()
        self.copywriter = CopywriterAgent()
        self.qa_director = QADirectorAgent()

    def produce_episode(
        self,
        theme: str,
        pillar: str = "الآداب والأخلاق (Manners)",
        upload_to_youtube: bool = False
    ) -> Dict[str, Any]:
        """Execute end-to-end studio production pipeline."""
        print("=" * 70, flush=True)
        print("🌟 TALES OF WONDER ANIMATION STUDIO - MULTI-AGENT PRODUCTION RUN 🌟", flush=True)
        print(f"Theme: {theme} | Pillar: {pillar}", flush=True)
        print("=" * 70, flush=True)

        today_str = datetime.date.today().isoformat()
        slug = theme.strip().replace(" ", "_")[:30]
        work_dir = self.output_dir / f"{today_str}_{slug}"
        work_dir.mkdir(parents=True, exist_ok=True)

        canvas_path = work_dir / "scene_canvas.jpg"
        audio_path = work_dir / "voiceover.wav"
        video_path = work_dir / "episode_shorts.mp4"

        # ----------------------------------------------------
        # Stage 1: Pedagogical Scriptwriting
        # ----------------------------------------------------
        print("\n--- [STAGE 1] DEPARTMENT OF SCRIPTWRITING & PEDAGOGY ---", flush=True)
        script_data = self.scriptwriter.run(theme=theme, pillar=pillar)

        # ----------------------------------------------------
        # Stage 2: Art Direction & Scene Preparation
        # ----------------------------------------------------
        print("\n--- [STAGE 2] DEPARTMENT OF ART DIRECTION & CHARACTER CONSISTENCY ---", flush=True)
        art_data = self.art_director.run(
            theme=theme,
            scene_hint=script_data.get("scene_suggestion"),
            output_path=canvas_path
        )

        # ----------------------------------------------------
        # Stage 3: Voice Acting & Sound Design
        # ----------------------------------------------------
        print("\n--- [STAGE 3] DEPARTMENT OF SOUND DESIGN & GEMINI TTS ---", flush=True)
        sound_data = self.sound_director.run(
            script_text=script_data["script"],
            output_audio_path=audio_path
        )

        # ----------------------------------------------------
        # Stage 4: Motion Animation & Camera Flow
        # ----------------------------------------------------
        print("\n--- [STAGE 4] DEPARTMENT OF MOTION ANIMATION & CAMERA FLOW ---", flush=True)
        motion_data = self.motion_animator.run(
            image_path=canvas_path,
            audio_path=audio_path,
            output_video_path=video_path,
            topic_title=script_data.get("title_ar", "حِكَايَاتُ العَجَائِب"),
            script_text=script_data.get("script", "")
        )

        # ----------------------------------------------------
        # Stage 5: Copywriting & Growth Strategy
        # ----------------------------------------------------
        print("\n--- [STAGE 5] DEPARTMENT OF COPYWRITING & YOUTUBE SEO ---", flush=True)
        copy_data = self.copywriter.run(
            title_ar=script_data["title_ar"],
            script=script_data["script"],
            lesson=script_data["lesson"],
            pillar=pillar
        )

        # ----------------------------------------------------
        # Stage 6: Executive Producer & Quality Assurance
        # ----------------------------------------------------
        print("\n--- [STAGE 6] EXECUTIVE PRODUCER QUALITY & COPPA AUDIT ---", flush=True)
        qa_report = self.qa_director.run(
            script_data=script_data,
            video_path=video_path,
            audio_path=audio_path,
            copy_data=copy_data
        )

        # ----------------------------------------------------
        # Stage 7: Optional Deployment & History Recording
        # ----------------------------------------------------
        upload_result = None
        if upload_to_youtube and qa_report["approved"]:
            print("\n--- [STAGE 7] AUTOMATED YOUTUBE DEPLOYMENT (DIRECT PUBLIC) ---", flush=True)
            upload_result = upload_video(
                video_path=video_path,
                title=copy_data["optimized_title"],
                description=copy_data["description"],
                tags=copy_data["tags"],
                privacy_status="public",
                made_for_kids=True,
                thumbnail_path=str(canvas_path)
            )

        # Record into history
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                hist = json.load(f)
            hist.setdefault("topics", []).append({
                "topic_key": slug,
                "date": today_str,
                "pillar": pillar,
                "title": script_data["title_ar"],
                "lesson": script_data["lesson"],
                "video_url": upload_result.get("video_url") if upload_result else None,
                "status": "studio_draft",
                "qa_score": qa_report["score"]
            })
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(hist, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70, flush=True)
        print("🎉 STUDIO PRODUCTION PIPELINE COMPLETED SUCCESSFULLY! 🎉", flush=True)
        print(f"🎬 Video: {video_path}", flush=True)
        print(f"🎙️ Audio: {audio_path}", flush=True)
        print(f"🏆 QA Score: {qa_report['score']}/100 ({qa_report['signoff_by']})", flush=True)
        if upload_result:
            print(f"📺 Private Link: {upload_result.get('video_url')}", flush=True)
        print("=" * 70, flush=True)

        return {
            "script": script_data,
            "art": art_data,
            "sound": sound_data,
            "motion": motion_data,
            "copy": copy_data,
            "qa": qa_report,
            "video_path": str(video_path),
            "upload_result": upload_result
        }
