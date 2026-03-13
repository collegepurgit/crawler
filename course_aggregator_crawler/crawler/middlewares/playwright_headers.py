"""Header helpers for Playwright requests."""

from __future__ import annotations


def playwright_context_kwargs() -> dict:
    """Default Playwright context configuration for JS pages."""
    return {
        "ignore_https_errors": True,
        "java_script_enabled": True,
        "user_agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
    }
