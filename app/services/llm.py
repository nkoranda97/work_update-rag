from app.core.openai_client import client

PROMPT_TMPL = """You are an expert assistant.

EMAIL SNIPPETS (with dates):
{ctx}
— End snippets —

Answer the user's question **referencing dates where relevant**.

{question}
"""


def answer_with_openai(question: str, snippets: list[str]) -> str:
    ctx = "\n\n".join(snippets)
    prompt = PROMPT_TMPL.format(ctx=ctx, question=question)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content
