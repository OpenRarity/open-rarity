def normalize_attribute_string(word: str) -> str:
    """Normalizes either attribute names or string attribute values.
    This is a helper function to ensure we are consistently normalizing
    by always lower casing and stripping input string.

    Parameters
    ----------
    word : str
        The string to normalize
        (this should be either attribute name or a string attribute value)

    Returns
    -------
    str
        normalized string
    """
    return word.lower().strip()
