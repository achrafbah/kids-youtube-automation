"""Copywriter & YouTube Growth Agent (قسم التأليف الإعلاني وسيو يوتيوب).
Crafts high-CTR titles, viral hooks, SEO descriptions, tags, and thumbnail slogans.
"""

import json
from typing import Dict, Any, List
from .base import BaseAgent

class CopywriterAgent(BaseAgent):
    """Specialist agent responsible for YouTube metadata, copywriting, and audience growth."""

    def __init__(self):
        super().__init__(
            name="Nadia Mansouri",
            role="Lead Growth Copywriter & YouTube Algorithm Strategist"
        )

    def generate_youtube_package(
        self,
        title_ar: str,
        script: str,
        lesson: str,
        pillar: str
    ) -> Dict[str, Any]:
        """Generate high-performing YouTube package using Gemini."""
        self.log(f"✍️ Crafting high-converting YouTube copy for: '{title_ar}'...")

        prompt = (
            f"أنت خبير محترف في خوارزميات يوتيوب وكتابة النصوص الإعلانية الجذابة (Copywriting) لقنوات الأطفال والتربية.\n"
            f"الموضوع: {title_ar}\n"
            f"المحور: {pillar}\n"
            f"الدرس المستفاد: {lesson}\n"
            f"النص الكرتوني: {script}\n\n"
            f"المطلوب إنشاء حزمة يوتيوب شورتس كاملة (YouTube Shorts Package) بالمعايير التالية:\n"
            f"1. **العنوان (Title)**: جذاب جداً يثير فضول الأمهات والأطفال، خفيف وأقل من 60 حرفاً، بدون تشكيل معقد، وينتهي وجوباً بـ #shorts.\n"
            f"2. **الوصف (Description)**: منظم وجميل جداً:\n"
            f"   - سطر أول خطاف غني بالكلمات المفتاحية (Hook).\n"
            f"   - نقاط الفائدة التعليمية للطفل.\n"
            f"   - دعوة للاشتراك للأمهات والأولياء.\n"
            f"   - 6 إلى 8 هاشتاغات مستهدفة تنتهي بـ #shorts #اطفال #كرتون #حكايات_العجائب.\n"
            f"3. **الكلمات الدلالية (Tags)**: قائمة من 15-25 كلمة دلالية شائعة جداً باللغة العربية والإنجليزية بدون رمز # إطلاقاً تملأ سقف يوتيوب.\n"
            f"4. **نص الصورة المصغرة (Thumbnail Hook)**: 3 إلى 4 كلمات قوية جداً ومحفزة للضغط توضع على الصورة.\n"
            f"5. **التعليق المثبت (Pinned Comment)**: سؤال تفاعلي يوجه للأولياء لتشجيعهم على التعليق.\n\n"
            f"أعد النتيجة حصراً بصيغة JSON:\n"
            f"{{\n"
            f'  "optimized_title": "العنوان المقترح الجذاب والمختصر #shorts",\n'
            f'  "description": "الوصف الكامل المنسق",\n'
            f'  "tags": ["تعليم اطفال", "كرتون اطفال", "رسوم متحركة", "arabic for kids", "اطفال"],\n'
            f'  "thumbnail_overlay_text": "نص الصورة المصغرة",\n'
            f'  "pinned_comment": "نص التعليق المثبت التفاعلي"\n'
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
            raise RuntimeError("All candidate Gemini models failed to generate copy.")

        try:
            data = json.loads(response.text)
            self.log(f"✅ Copywriting package crafted: Title: '{data.get('optimized_title')}'")
            return data
        except Exception as e:
            self.log(f"⚠️ JSON parsing error: {e}. Using structured fallback.")
            return {
                "optimized_title": f"{title_ar} #shorts",
                "description": f"مرحباً بكم في حكايات العجائب (Tales of Wonder)!\n\n💡 {lesson}\n\n#shorts #أطفال #تربية_الطفل #كرتون_اطفال #تعليم_اطفال",
                "tags": ["تعليم اطفال", "كرتون اطفال", "اطفال", "رسوم متحركة", "حكايات العجائب", "tales of wonder", "arabic for kids"],
                "thumbnail_overlay_text": "شاهد المفاجأة! ✨",
                "pinned_comment": "هل تطبقون هذه العادة مع أطفالكم؟ شاركونا في التعليقات! 👇"
            }

    def run(
        self,
        title_ar: str,
        script: str,
        lesson: str,
        pillar: str
    ) -> Dict[str, Any]:
        """Run copywriter agent."""
        return self.generate_youtube_package(
            title_ar=title_ar,
            script=script,
            lesson=lesson,
            pillar=pillar
        )
