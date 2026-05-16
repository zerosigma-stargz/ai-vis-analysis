"""
core/currency_cleaner.py — Currency detection and cleaning utilities.

Provides functions to detect currency-formatted columns in a pandas Series
and clean them into float64 values suitable for numerical analysis.
"""

import re

import pandas as pd

# ---------------------------------------------------------------------------
# Regex pattern for detecting currency symbols (prefix and suffix)
# Supports: Rp, $, €, £, ¥, USD, IDR, EUR, GBP, JPY
# ---------------------------------------------------------------------------
CURRENCY_PATTERN = re.compile(
    r"""
    (?:                          # Simbol di depan (prefix)
        Rp\.?\s*|                # Rupiah: "Rp", "Rp."
        \$\s*|                   # Dollar: "$"
        €\s*|                    # Euro: "€"
        £\s*|                    # Pound: "£"
        ¥\s*|                    # Yen: "¥"
        USD\s*|                  # USD literal
        IDR\s*|                  # IDR literal
        EUR\s*|                  # EUR literal
        GBP\s*|                  # GBP literal
        JPY\s*                   # JPY literal
    )
    [\d.,]+                      # Angka dengan pemisah
    |
    [\d.,]+                      # Angka dengan pemisah
    (?:\s*(?:USD|IDR|EUR|GBP|JPY))  # Simbol di belakang (suffix)
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Regex to strip currency symbol prefixes from a value string
_PREFIX_PATTERN = re.compile(
    r"^(?:Rp\.?\s*|\$\s*|€\s*|£\s*|¥\s*|USD\s*|IDR\s*|EUR\s*|GBP\s*|JPY\s*)",
    re.IGNORECASE,
)

# Regex to strip currency symbol suffixes from a value string
_SUFFIX_PATTERN = re.compile(
    r"\s*(?:USD|IDR|EUR|GBP|JPY)\s*$",
    re.IGNORECASE,
)


def detect_currency_pattern(series: pd.Series) -> bool:
    """Detect whether a Series contains currency-formatted values.

    Only operates on Series of dtype ``object`` or ``StringDtype`` (string
    columns). Returns ``True`` as soon as a single non-null value matches the
    currency pattern, making it efficient for large Series.

    Parameters
    ----------
    series:
        The pandas Series to inspect.

    Returns
    -------
    bool
        ``True`` if at least one value matches a known currency pattern,
        ``False`` otherwise (including when the Series dtype is not a string
        type).

    Requirements: 13.1
    """
    # Accept both legacy object dtype and newer pandas StringDtype
    if series.dtype != object and not isinstance(series.dtype, pd.StringDtype):
        return False

    for value in series.dropna():
        if CURRENCY_PATTERN.search(str(value)):
            return True

    return False


def clean_currency_column(series: pd.Series) -> tuple[pd.Series, int]:
    """Clean a currency-formatted Series and convert it to float64.

    Processing steps:
    1. Remove currency symbol prefixes (``Rp``, ``$``, ``€``, ``£``, ``¥``,
       ``USD``, ``IDR``, ``EUR``, ``GBP``, ``JPY``) and suffixes.
    2. Detect number format: if a dot appears *before* a comma in any value,
       the column uses Indonesian/European notation (dot = thousands separator,
       comma = decimal separator).
    3. Remove thousands separators and replace the decimal comma with a dot
       (or remove thousands commas for US format).
    4. Convert to ``float64`` using ``pd.to_numeric(errors='coerce')``.
    5. Count and return the number of *new* NaN values introduced by the
       conversion (i.e. values that were not already NaN in the original
       Series but became NaN after conversion).

    Parameters
    ----------
    series:
        The pandas Series to clean. Non-string values are coerced to strings
        before processing.

    Returns
    -------
    tuple[pd.Series, int]
        A tuple of:
        - The cleaned Series with dtype ``float64``.
        - The count of new NaN values introduced by the conversion.

    Requirements: 13.4
    """
    # Work on a string copy; preserve original NaN positions for counting later
    original_na_mask = series.isna()

    def _strip_symbols(value: str) -> str:
        """Remove prefix and suffix currency symbols from a string value."""
        value = _PREFIX_PATTERN.sub("", value)
        value = _SUFFIX_PATTERN.sub("", value)
        return value.strip()

    def _is_indonesian_format(value: str) -> bool:
        """Return True if the value uses Indonesian/European notation.

        Two cases are detected:
        1. Dot appears before a comma (e.g. "1.500,50") — classic Indonesian format.
        2. Multiple dots with no comma (e.g. "1.500.000") — dots are thousands
           separators; there is no decimal part.
        """
        dot_pos = value.find(".")
        comma_pos = value.find(",")
        # Case 1: dot before comma
        if dot_pos != -1 and comma_pos != -1 and dot_pos < comma_pos:
            return True
        # Case 2: more than one dot and no comma → dots are thousands separators
        if value.count(".") > 1 and comma_pos == -1:
            return True
        return False

    # Strip symbols from all non-null string values
    cleaned = series.copy().astype(object)
    for idx in series.index:
        if pd.isna(series[idx]):
            continue
        cleaned[idx] = _strip_symbols(str(series[idx]))

    # Detect number format by scanning the first few non-null cleaned values
    use_indonesian_format = False
    for idx in cleaned.index:
        if pd.isna(cleaned[idx]):
            continue
        val = str(cleaned[idx])
        if _is_indonesian_format(val):
            use_indonesian_format = True
            break

    # Normalise number separators
    def _normalise(value: str) -> str:
        if use_indonesian_format:
            # dot = thousands separator → remove; comma = decimal → replace with dot
            value = value.replace(".", "")
            value = value.replace(",", ".")
        else:
            # comma = thousands separator → remove; dot = decimal → keep
            value = value.replace(",", "")
        return value

    normalised = cleaned.copy()
    for idx in cleaned.index:
        if pd.isna(cleaned[idx]):
            continue
        normalised[idx] = _normalise(str(cleaned[idx]))

    # Convert to float64, coercing unparseable values to NaN
    result = pd.to_numeric(normalised, errors="coerce").astype("float64")

    # Count only *new* NaN values (not those already present in the original)
    new_na_mask = result.isna() & ~original_na_mask
    nan_count = int(new_na_mask.sum())

    return result, nan_count
