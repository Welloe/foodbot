import os
from openai import OpenAI
from django.core.management.base import BaseCommand
from chatbot.models import ChatResponse
from django.utils import timezone

# chatbot/management/commands/simulate_chats.py

def simulate_gpt_chats(n=100, stdout=None):
    from openai import OpenAI
    from chatbot.models import ChatResponse
    from django.utils import timezone
    import os

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

    prompt = "What are your top 3 favorite foods? Pick ones that are uncommon and avoid repeating the usual answers. Answers must be simple and short."

    for i in range(n):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.1
            )
            reply = response.choices[0].message.content.strip()

            ChatResponse.objects.create(
                role="B",
                message=reply,
                is_vegetarian_or_vegan=is_vegetarian_or_vegan(reply),
                created_at=timezone.now()
            )

            if stream:
                one_liner = " ".join(
                    line.strip() for line in reply.splitlines() if line.strip()
                )
                yield f"{i+1:03d}/100 → {one_liner}"
        except Exception as e:
            if stream:
                yield f"{i+1:03d}/100 → ❌ Error: {e}"
            continue

# keep your Command class as is
class Command(BaseCommand):
    help = "Simulates 100 GPT A→B real OpenAI conversations."

    def handle(self, *args, **kwargs):
        simulate_gpt_chats(stdout=self.stdout)

