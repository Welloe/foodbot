import os
from django.utils import timezone
from openai import OpenAI

from chatbot.models import ChatResponse, BlacklistedKeyword

# Initialize OpenAI client globally to avoid redundant setups
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def simulate_gpt_chats(n=100, stream=False):
    """
    Simulate 'n' GPT chat completions asking for top 3 favorite foods.
    Classify responses as vegetarian/vegan or not based on keywords.
    If 'stream' is True, yield each response in real-time.
    """

    def is_vegetarian_or_vegan(text):
        """
        Check if the given text mentions any non-vegetarian or non-vegan ingredients.
        Combines hardcoded base keywords with dynamically learned keywords from DB.
        """
        base_keywords = [
            "chicken", "beef", "pork", "bacon", "steak", "fish", "shrimp", "lamb", "meat",
            "salmon", "turkey", "duck", "anchovy", "tuna", "prosciutto", "ribs",
            "sausage", "ham", "veal", "pepperoni", "mutton", "crab", "lobster", "octopus",
            "cheese", "milk", "cream", "butter", "yogurt", "egg", "mayonnaise", "honey"
        ]
        db_keywords = BlacklistedKeyword.objects.values_list("keyword", flat=True)
        all_keywords = set(base_keywords) | set(db_keywords)
        return not any(word in text.lower() for word in all_keywords)

    # Clear existing chat responses before starting
    ChatResponse.objects.all().delete()

    # Define the prompt for the AI
    prompt = (
        "What are your top 3 favorite foods? Pick ones that are uncommon and avoid "
        "repeating the usual answers. Also make it short and simple."
    )

    # Generate and store 'n' responses
    for i in range(n):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.1
            )
            reply = response.choices[0].message.content.strip()

            # Save response to database
            ChatResponse.objects.create(
                role="B",
                message=reply,
                is_vegetarian_or_vegan=is_vegetarian_or_vegan(reply),
                created_at=timezone.now()
            )

            if stream:
                yield reply  # Yield each message if streaming enabled

        except Exception as e:
            if stream:
                yield f"❌ Error: {e}"


def self_learn_from_non_veg_responses():
    """
    Analyze non-vegetarian/vegan responses to discover and learn new blacklisted keywords.
    Updates the database and rechecks previously classified vegetarian/vegan responses.
    Returns a list of newly discovered keywords.
    """
    flagged = ChatResponse.objects.filter(is_vegetarian_or_vegan=False)[:25]
    new_keywords = []

    for response in flagged:
        # Step 1: Extract potential non-veg ingredients
        extraction_prompt = (
            "You are an expert on vegetarian diets. From the following food description, "
            "extract all ingredients or words that are NOT vegetarian or vegan friendly:\n\n"
            f'"{response.message}"\n\nReturn ONLY a comma-separated list of those words.'
        )

        try:
            result = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.3
            )

            words = result.choices[0].message.content.strip().lower().split(",")

            for word in map(str.strip, words):
                if not word or BlacklistedKeyword.objects.filter(keyword=word).exists():
                    continue

                # Step 2: Verify each extracted word with OpenAI
                verify_prompt = f"Is '{word}' vegetarian or vegan friendly? Reply only with Yes or No."
                check = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": verify_prompt}],
                    temperature=0
                )
                answer = check.choices[0].message.content.strip().lower()

                if answer == "no":
                    BlacklistedKeyword.objects.create(keyword=word)
                    new_keywords.append(word)

        except Exception as e:
            print(f"❌ Error during OpenAI analysis: {e}")
            continue

    # Step 3: Recheck existing responses marked as vegetarian/vegan
    if new_keywords:
        all_blacklisted = list(BlacklistedKeyword.objects.values_list("keyword", flat=True))
        for response in ChatResponse.objects.filter(is_vegetarian_or_vegan=True):
            if any(word in response.message.lower() for word in all_blacklisted):
                response.is_vegetarian_or_vegan = False
                response.save()

    return new_keywords
