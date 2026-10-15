"""Scriptwriter & Educational Pedagogue Agent (قسم السيناريو والبيداغوجيا).
Generates pedagogical Arabic scripts (ages 3-10) with complete diacritics (tashkeel).
"""

import json
from typing import Dict, Any, Optional
from .base import BaseAgent

class ScriptwriterAgent(BaseAgent):
    """Specialist agent responsible for storyline, curriculum pillars, and Arabic scriptwriting."""

    def __init__(self):
        super().__init__(
            name="Layla Al-Khatib",
            role="Lead Pedagogical Scriptwriter & Arabic Linguist"
        )
        self.curriculum_file = self.data_dir / "topics_history.json"

    def generate_custom_script(self, theme: str, pillar: str = "الآداب والأخلاق") -> Dict[str, Any]:
        """Generate a fresh educational script using Gemini with full Arabic diacritics."""
        self.log(f"✍️ Drafting original pedagogical script for theme: '{theme}' under pillar '{pillar}'...")
        
        prompt = (
            f"أنت كاتب سيناريو محترف للأطفال في قناة يوتيوب تعليمية رائدة (حكايات العجائب / Tales of Wonder).\n"
            f"المطلوب: كتابة نص كرتوني قصير وممتع جداً للأطفال من 3 إلى 10 سنوات (مدة القراءة 25-35 ثانية).\n"
            f"المحور: {pillar}\n"
            f"الموضوع: {theme}\n"
            f"الشخصية المتحدثة: ليث (Leo) - طفل شجاع ذكي ومحبوب (6 سنوات).\n\n"
            f"شروط كتابة النص الصارمة:\n"
            f"1. لغة عربية فصحى مبسطة وجميلة جداً.\n"
            f"2. التشكيل التام بالحركات (فتحة، ضمة، كسرة، سكون، شدة، تنوين) لضمان النطق السليم 100% عبر الذكاء الاصطناعي.\n"
            f"3. بنية النص:\n"
            f"   - جملة تحية حماسية ومرحة للأصدقاء.\n"
            f"   - الموقف التعليمي أو النصيحة بشكل محبب وملموس.\n"
            f"   - عبارة تفاعلية تشجع الطفل على الترديد أو التطبيق (مثل: رددوا معي!).\n"
            f"   - خاتمة تشجيعية دافئة.\n\n"
            f"أعد الإجابة بصيغة JSON فقط بهذه الحقول:\n"
            f"{{\n"
            f'  "title_ar": "عنوان الحلقة بالعربية مع الإيموجي",\n'
            f'  "script": "نص السيناريو الكامل مع التشكيل التام بالحركات",\n'
            f'  "lesson": "الدرس البيداغوجي المستفاد في سطر واحد",\n'
            f'  "scene_suggestion": "وصف المكان والأدوات المناسبة للمشهد"\n'
            f"}}"
        )

        candidate_models = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
        response = None
        for model_name in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                if response and response.text:
                    break
            except Exception as e:
                self.log(f"Model {model_name} unavailable ({e}), trying next candidate...")

        if not response or not response.text:
            raise RuntimeError("All candidate Gemini models failed to generate script.")

        try:
            data = json.loads(response.text)
            self.log(f"✅ Script created successfully: '{data.get('title_ar')}'")
            return data
        except Exception as e:
            self.log(f"⚠️ JSON parse error, returning fallback format: {e}")
            return {
                "title_ar": theme,
                "script": response.text,
                "lesson": f"أهمية {theme} في حياة الأطفال.",
                "scene_suggestion": "غرفة صف كرتونية ملونة"
            }

    def run(self, theme: Optional[str] = None, pillar: str = "الآداب والأخلاق") -> Dict[str, Any]:
        """Main agent runner."""
        if theme:
            return self.generate_custom_script(theme, pillar)
        
        # Default topic generator
        return self.generate_custom_script(
            theme="مساعدة الأصدقاء والتعاون في المدرسة",
            pillar="الآداب والأخلاق (Manners)"
        )
