"""
backend/banking/utils.py — Account-detection utilities.

This module contains non-model business logic used during transaction
imports: inferring an account type from uploaded CSV filenames.

Account type detection relies on canonical handler keys defined in
banking.constants.HandlerKeys. These keys are system-defined, seeded via
data migrations, and resolved at runtime through the account handler
registry.

Transaction persistence (upsert_transactions) has moved to
transactions/utils.py — banking owns account/handler concerns only;
anything that creates or queries Transaction rows belongs in the
transactions app.
"""

from banking.constants import HandlerKeys

# ── Account detection ─────────────────────────────────────────────────────────

# Maps filename substrings to handler_key values in ACCOUNT_HANDLERS.
# Order matters — more specific patterns should come first.
FILE_DETECTION_MAP = {
    '360Checking': HandlerKeys.CO_CHECKING,
    '360PerformanceSavings': HandlerKeys.CO_SAVINGS,
    'transaction_download': HandlerKeys.CO_QUICKSILVER,
    'SOFI-Checking': HandlerKeys.SOFI_CHECKING,
    'SOFI-Savings': HandlerKeys.SOFI_SAVINGS,
    'WF-Checking': HandlerKeys.WF_CHECKING,
    'WF-Savings': HandlerKeys.WF_SAVINGS,
    'activity': HandlerKeys.AMEX_DELTA,
    'Chase': HandlerKeys.CHASE,
    'Discover': HandlerKeys.DISCOVER,
}


def detect_account_type(filename: str) -> str | None:
    """
    Attempt to detect the account type from a CSV filename.

    Returns the handler_key string if detected, or None if unrecognized.
    The result is always shown to the user for confirmation before import.
    """
    for substring, handler_key in FILE_DETECTION_MAP.items():
        if substring in filename:
            return handler_key
    return None
