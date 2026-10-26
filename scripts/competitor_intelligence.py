"""Competitor Intelligence & Algorithmic Self-Learning Agent.
Analyzes top-performing Arabic kids Shorts for each topic, audits our own channel
velocity, and distills high-CTR hooks, proven tags, and system optimization rules.
"""

import os
import re
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from google import genai

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LEARNED_PATTERNS_FILE = DATA_DIR / "learned_patterns.json"
TOPICS_FILE = DATA_DIR / "topics_history.json"
ENV_FILE = BASE_DIR / ".env"

class CompetitorIntelligenceAgent:
    """Investigates YouTube search algorithm trends and evolves the content strategy."""

    def __init__(self, youtube_service=None):
        self.youtube = youtube_service
        self._client = None

    def _get_api_key(self) -> str:
        if ENV_FILE.exists():
            for line in open(ENV_FILE, encoding="utf-8"):
                if line.startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1]
        return os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA")

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._get_api_key())
        return self._client

    def _get_youtube(self):
        if self.youtube is None:
            try:
                from youtube_uploader import get_authenticated_service
                self.youtube = get_authenticated_service()
            except Exception as e:
                print(f"⚠️ [INTEL] Notice initializing YouTube service: {e}")
                self.youtube = None
        return self.youtube

    def research_competitors(self, search_query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Fetch top-performing Arabic Kids Shorts for the given topic using 1 search call."""
        yt = self._get_youtube()
        if not yt:
            return []

        try:
            clean_q = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', search_query).strip()
            clean_q = re.sub(r'[^\w\s]', ' ', clean_q)
            query_str = f"{clean_q} كرتون اطفال shorts"

            print(f"🔍 [INTEL] Searching YouTube for competitor viral trends: '{query_str}'...", flush=True)
            search_req = yt.search().list(
                part="snippet",
                q=query_str,
                type="video",
                relevanceLanguage="ar",
                order="relevance",
                maxResults=max_results
            )
            search_res = search_req.execute()
            items = search_res.get("items", [])
            if not items:
                return []

            video_ids = [it["id"]["videoId"] for it in items if "videoId" in it.get("id", {})]
            if not video_ids:
                return []

            # Fetch rich metrics in 1 batched call (costs only 1 quota point)
            details_req = yt.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids)
            )
            details_res = details_req.execute()

            competitors = []
            for item in details_res.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                competitors.append({
                    "video_id": item.get("id"),
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "tags": snippet.get("tags", [])[:8],
                    "url": f"https://youtu.be/{item.get('id')}"
                })

            print(f"✅ [INTEL] Successfully analyzed {len(competitors)} viral competitor benchmark(s).", flush=True)
            return competitors

        except Exception as e:
            print(f"⚠️ [INTEL] YouTube competitor search notice: {e}", flush=True)
            return []

    def audit_our_channel_feedback(self) -> Dict[str, Any]:
        """Audit the real-time velocity and engagement of recent videos on our own channel."""
        if not TOPICS_FILE.exists():
            return {}

        try:
            with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            topics = history.get("topics", [])
            published = [t for t in topics if t.get("video_url") and t.get("status") in ["public_published", "published"]]
            if not published:
                return {"tracked_count": 0}

            recent = published[-3:]
            yt = self._get_youtube()
            if not yt:
                return {"tracked_count": len(published), "recent_titles": [r.get("title") for r in recent]}

            video_ids = []
            for r in recent:
                m = re.search(r"(?:youtu\.be/|v=|shorts/)([A-Za-z0-9_-]{11})", r.get("video_url", ""))
                if m:
                    video_ids.append(m.group(1))

            if not video_ids:
                return {"tracked_count": len(published)}

            v_res = yt.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()
            tracked_stats = []
            for item in v_res.get("items", []):
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                tracked_stats.append({
                    "title": snippet.get("title"),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0))
                })

            return {
                "tracked_count": len(published),
                "recent_performance": tracked_stats
            }
        except Exception as e:
            print(f"⚠️ [INTEL] Channel feedback audit notice: {e}", flush=True)
            return {}

    def synthesize_viral_patterns(
        self,
        topic: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        channel_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Gemini AI (with heuristic fallback) to distill actionable SEO hooks and lessons."""
        if not competitors:
            # Deterministic fallback when no competitor data is retrieved
            return {
                "proven_keywords": [topic.get("title_ar", ""), "كرتون اطفال", "تعليم الروضة"],
                "suggested_tags": ["تعليم اطفال", "كرتون اطفال", "حكايات العجائب", "shorts"],
                "viral_hook_pattern": "Energetic preschool cartoon inquiry hook",
                "system_learning_rule": "Prioritize energetic question hooks under 50 characters."
            }

        prompt = f"""
You are the Chief YouTube Algorithm Strategist for Arabic Preschool & Educational Cartoons (Tales of Wonder | حكايات العجائب).

Current Episode Topic:
- Title: {topic.get('title_ar')}
- Pillar: {topic.get('pillar')}
- Lesson: {topic.get('lesson')}

Top-Ranking Competitor Arabic Shorts on this exact topic:
{json.dumps(competitors, ensure_ascii=False, indent=2)}

Our Channel's Recent Feedback:
{json.dumps(channel_feedback, ensure_ascii=False, indent=2)}

Analyze what makes these competitor titles and keywords rank high on YouTube Shorts.
Return ONLY a valid JSON object (no markdown, no backticks) with:
1. "proven_keywords": List of 5-8 high-converting Arabic keyword phrases observed in competitors.
2. "suggested_tags": List of 6-8 clean Arabic tags (without '#', without underscores) that best categorize this topic for YouTube search algorithms.
3. "suggested_title_hook": A high-CTR, punchy title under 55 characters ending with "#shorts" that uses proven phrasing from competitors.
4. "viral_hook_pattern": 1 sentence explaining the pattern (e.g. "Song/rhyme format", "Curiosity question hook", "Action imperative").
5. "system_learning_rule": 1 concise rule to store in our algorithm memory for future episodes.
"""
        candidate_models = ["gemini-3.8-flash", "gemini-flash-latest"]
        for m in candidate_models:
            try:
                resp = self.client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if resp and resp.text:
                    raw = resp.text.strip()
                    if raw.startswith("```"):
                        raw = re.sub(r"^```(?:json)?", "", raw)
                        raw = re.sub(r"```$", "", raw).strip()
                    parsed = json.loads(raw)
                    print(f"💡 [INTEL] Strategy Synthesized: Rule -> '{parsed.get('system_learning_rule')}'", flush=True)
                    return parsed
            except Exception as e:
                print(f"⚠️ [INTEL] Notice with {m}: {e}", flush=True)
                continue

        # Heuristic fallback: extract tags and title terms from competitors directly
        combined_tags = []
        for c in competitors:
            for t in c.get("tags", []):
                cleaned = t.replace("#", "").replace("_", " ").strip()
                if cleaned and cleaned not in combined_tags:
                    combined_tags.append(cleaned)

        return {
            "proven_keywords": [c.get("title", "") for c in competitors][:3],
            "suggested_tags": combined_tags[:8] or ["تعليم اطفال", "كرتون اطفال", "حكايات العجائب"],
            "suggested_title_hook": f"{topic.get('title_ar', '')[:48]} #shorts",
            "viral_hook_pattern": "Competitor keyword frequency alignment",
            "system_learning_rule": "Incorporate high-frequency competitor search terms in first 3 lines."
        }

    def save_learned_memory(self, topic_key: str, insights: Dict[str, Any], competitors: List[Dict[str, Any]]):
        """Append discoveries to data/learned_patterns.json for long-term algorithmic evolution."""
        memory = {
            "total_cycles": 0,
            "learned_rules": [],
            "recent_insights": []
        }
        if LEARNED_PATTERNS_FILE.exists():
            try:
                with open(LEARNED_PATTERNS_FILE, "r", encoding="utf-8") as f:
                    memory = json.load(f)
            except Exception:
                pass

        new_rule = insights.get("system_learning_rule")
        if new_rule and new_rule not in memory.get("learned_rules", []):
            memory.setdefault("learned_rules", []).append(new_rule)

        # Keep latest 25 rules
        memory["learned_rules"] = memory["learned_rules"][-25:]
        memory["total_cycles"] = memory.get("total_cycles", 0) + 1

        insight_entry = {
            "topic_key": topic_key,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "hook_pattern": insights.get("viral_hook_pattern"),
            "suggested_title": insights.get("suggested_title_hook"),
            "proven_keywords": insights.get("proven_keywords", []),
            "competitors_analyzed": [
                {"title": c.get("title"), "views": c.get("views"), "channel": c.get("channel")}
                for c in competitors
            ]
        }
        memory.setdefault("recent_insights", []).append(insight_entry)
        memory["recent_insights"] = memory["recent_insights"][-15:]

        try:
            with open(LEARNED_PATTERNS_FILE, "w", encoding="utf-8") as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
            print(f"🧠 [INTEL] Algorithmic memory updated! Total active rules: {len(memory['learned_rules'])}", flush=True)
        except Exception as e:
            print(f"⚠️ [INTEL] Notice saving learned memory: {e}", flush=True)

    def analyze_and_learn(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point: executes complete research, audit, and pattern distillation workflow."""
        search_query = topic.get("title_ar", "")
        competitors = self.research_competitors(search_query=search_query, max_results=3)
        channel_feedback = self.audit_our_channel_feedback()
        insights = self.synthesize_viral_patterns(topic, competitors, channel_feedback)
        self.save_learned_memory(topic.get("topic_key", "general"), insights, competitors)
        return insights
