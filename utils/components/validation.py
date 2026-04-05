"""Utilities for validating data."""

import string


def validate_id(text: str) -> bool:
    """
    Validate that the given text is a valid ID.

    A valid ID must meet the following criteria:
        - Must be a non-empty string.
        - Must start with a letter (a-z or A-Z).
        - Can only contain letters, digits (0-9), hyphens (-), and
        underscores (_).

    Args:
        text (str): The text to validate as an ID.

    Returns:
        bool: True if the text is a valid ID, False otherwise.
    """
    if not isinstance(text, str) or not text:
        return False

    first_characters = set(string.ascii_letters)
    subsequent_characters = first_characters.union(
        set(string.digits + "-" + "_")
    )

    if text[0] not in first_characters:
        return False

    if set(text[1:]) - set(subsequent_characters):
        return False

    return True
