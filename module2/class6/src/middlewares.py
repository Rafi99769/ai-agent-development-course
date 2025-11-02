"""Middlewares for the e-commerce agent."""

from langchain.agents.middleware import (
    SummarizationMiddleware,
    PIIMiddleware,
    HumanInTheLoopMiddleware,
)
from langchain_core.language_models import BaseChatModel


def get_pii_middleware() -> PIIMiddleware:
    """Create PII middleware to redact emails before sending to LLM.

    Returns:
        Configured PIIMiddleware instance
    """
    return PIIMiddleware(
        "email",
        strategy="redact",
        apply_to_input=True,
    )


def get_human_in_the_loop_middleware() -> HumanInTheLoopMiddleware:
    """Create human-in-the-loop middleware for order confirmation.

    Returns:
        Configured HumanInTheLoopMiddleware instance
    """
    return HumanInTheLoopMiddleware(
        interrupt_on={
            "create_order": {
                "allowed_decisions": ["approve", "edit", "reject"],
                "description": (
                    "Please review and confirm your order details. "
                    "You can approve, edit (name/email), or reject the order."
                ),
            },
        },
        description_prefix="Order confirmation pending",
    )


def get_summarization_middleware(model: BaseChatModel) -> SummarizationMiddleware:
    """Create summarization middleware to manage conversation length.

    Args:
        model: The LLM model to use for summarization

    Returns:
        Configured SummarizationMiddleware instance
    """
    return SummarizationMiddleware(
        model=model,
        max_tokens_before_summary=2000,
        messages_to_keep=5,
    )


def get_all_middlewares(smol_llm: BaseChatModel):
    """Get all middlewares for the e-commerce agent.

    Args:
        smol_llm: The LLM model to use for summarization

    Returns:
        List of middleware instances
    """
    return [
        get_pii_middleware(),
        get_human_in_the_loop_middleware(),
        get_summarization_middleware(smol_llm),
    ]
