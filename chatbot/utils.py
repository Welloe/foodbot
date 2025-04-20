import os
from openai import OpenAI
from django.utils import timezone
from chatbot.models import ChatResponse,BlacklistedKeyword

def simulate_gpt_chats(n=100, stream=False):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def is_vegetarian_or_vegan(text):
        base_keywords = [
            "chicken", "beef", "pork", "bacon", "steak", "fish", "shrimp", "lamb", "meat",
            "salmon", "turkey", "duck", "anchovy", "tuna", "prosciutto", "ribs",
            "sausage", "ham", "veal", "pepperoni", "mutton", "crab", "lobster", "octopus",
            "cheese", "milk", "cream", "butter", "yogurt", "egg", "mayonnaise", "honey"
        ]
        db_keywords = BlacklistedKeyword.objects.values_list("keyword", flat=True)
        all_keywords = set(base_keywords) | set(db_keywords)
        return not any(word in text.lower() for word in all_keywords)

    ChatResponse.objects.all().delete()
    prompt = "What are your top 3 favorite foods? Pick ones that are uncommon and avoid repeating the usual answers. Also make it short and simple."

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
                yield reply  # Yield each message if streaming

        except Exception as e:
            if stream:
                yield f"❌ Error: {e}"

def self_learn_from_non_veg_responses():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    flagged = ChatResponse.objects.filter(is_vegetarian_or_vegan=False)[:25]
    new_keywords = []

    for response in flagged:
        prompt = (
            "You are an expert on vegetarian diets. From the following food description, "
            "extract all ingredients or words that are NOT vegetarian or vegan friendly:\n\n"
            f'"{response.message}"\n\nReturn ONLY a comma-separated list of those words.'
        )

        try:
            result = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            words = result.choices[0].message.content.strip().lower().split(",")
            for word in map(str.strip, words):
                if word and not BlacklistedKeyword.objects.filter(keyword=word).exists():
                    BlacklistedKeyword.objects.create(keyword=word)
                    new_keywords.append(word)

        except Exception as e:
            print(f"❌ Error during OpenAI analysis: {e}")
            continue

    return new_keywords

