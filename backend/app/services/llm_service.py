import ollama

from app.services.prompt_service import build_prompt


def generate_answer(question: str, context: str, history: list) -> str:

    prompt = build_prompt(
        question,
        context,
        history
    )

    response = ollama.chat(
        model="gemma2:2b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]