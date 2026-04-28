from collections.abc import Generator
from pathlib import Path

from app.core.config import settings

_llm = None


def _get_llm():
    global _llm

    if _llm is not None:
        return _llm

    if not Path(settings.model_path).exists():
        return None

    from llama_cpp import Llama

    _llm = Llama(
        model_path=settings.model_path,
        n_ctx=settings.llm_n_ctx,
        n_threads=settings.llm_n_threads,
    )
    return _llm


def build_prompt(user_message: str) -> str:
    return (
        "You are a helpful assistant. Answer clearly and briefly.\n\n"
        f"User: {user_message}\n"
        "Assistant:"
    )


def ask_llm(user_message: str) -> str:
    llm = _get_llm()
    if llm is None:
        return (
            "mock llm answer: model.gguf was not found, "
            "but the app pipeline works. Add a GGUF model to enable real answers."
        )

    result = llm(
        build_prompt(user_message),
        max_tokens=300,
        stream=False,
        stop=["User:"],
    )
    return result["choices"][0]["text"].strip()


def stream_llm(user_message: str) -> Generator[str, None, None]:
    llm = _get_llm()
    if llm is None:
        text = (
            "mock llm answer: model.gguf was not found, "
            "but streaming endpoint works."
        )
        for token in text.split(" "):
            yield token + " "
        return

    stream = llm(
        build_prompt(user_message),
        max_tokens=300,
        stream=True,
        stop=["User:"],
    )

    for chunk in stream:
        token = chunk["choices"][0]["text"]
        if token:
            yield token
