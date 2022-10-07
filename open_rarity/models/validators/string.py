def clean_lower_string(value: str | None) -> str | None:
    """Normalizes either attribute names or string attribute values.
    This is a helper function to ensure we are consistently normalizing
    by always lower casing and stripping input string.

    Parameters
    ----------
    value : str
        The string to normalize
        (this should be either attribute name or a string attribute value)

    Returns
    -------
    str
        normalized string
    """
    if value is None:
        return value
    return value.lower().strip()
