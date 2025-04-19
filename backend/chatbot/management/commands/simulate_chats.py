import os
from openai import OpenAI
from django.core.management.base import BaseCommand
from chatbot.models import ChatResponse
from django.utils import timezone

class Command(BaseCommand):
    help = "Simulates 100 GPT A→B real OpenAI conversations."

    def handle(self, *args, **kwargs):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        def is_vegetarian_or_vegan(text):
            non_veg_keywords = [
                "chicken", "beef", "pork", "bacon", "steak", "fish", "shrimp", "lamb", "meat",
                "salmon", "turkey", "duck", "anchovy", "tuna", "prosciutto", "ribs",
                "sausage", "ham", "veal", "pepperoni", "mutton", "crab", "lobster", "octopus"
            ]
            non_vegan_keywords = [
                "cheese", "milk", "cream", "butter", "yogurt", "egg", "mayonnaise", "honey"
            ]

            text_lower = text.lower()
            return not any(word in text_lower for word in non_veg_keywords + non_vegan_keywords)


        prompt = "What are your top 3 favorite foods? Pick ones that are uncommon or regional, and avoid repeating the usual answers."

        for i in range(100):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1.1  # add some randomness
                )
                reply = response.choices[0].message.content.strip()

                ChatResponse.objects.create(
                    role="B",
                    message=reply,
                    is_vegetarian_or_vegan=is_vegetarian_or_vegan(reply),
                    created_at=timezone.now()
                )

                self.stdout.write(f"[{i+1}/100] ✅ Reply saved: {reply[:30]}...")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[{i+1}/100] ❌ Error: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS("✅ 100 real GPT responses saved."))
