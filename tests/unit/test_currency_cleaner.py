"""
Unit tests for core/currency_cleaner.py

Tests cover:
- Detection of various currency symbols (Rp, $, €, £, ¥, USD, IDR, EUR, GBP, JPY)
- Cleaning Indonesian format (dot thousands, comma decimal) e.g. "Rp 1.500.000,50"
- Cleaning US format (comma thousands, dot decimal) e.g. "$1,500.00"
- Handling values that cannot be converted (NaN count)
- Pure numeric series should NOT be detected as currency (Property 10)
"""

import math

import pandas as pd
import pytest

from core.currency_cleaner import clean_currency_column, detect_currency_pattern


# ---------------------------------------------------------------------------
# detect_currency_pattern — symbol detection
# ---------------------------------------------------------------------------


class TestDetectCurrencyPattern:
    """Tests for detect_currency_pattern()."""

    def test_detects_rp_prefix(self):
        series = pd.Series(["Rp 1.500.000", "Rp 200.000"])
        assert detect_currency_pattern(series) is True

    def test_detects_rp_dot_prefix(self):
        series = pd.Series(["Rp. 1.500.000"])
        assert detect_currency_pattern(series) is True

    def test_detects_dollar_prefix(self):
        series = pd.Series(["$1,500.00", "$200.00"])
        assert detect_currency_pattern(series) is True

    def test_detects_euro_prefix(self):
        series = pd.Series(["€1.500,50"])
        assert detect_currency_pattern(series) is True

    def test_detects_pound_prefix(self):
        series = pd.Series(["£1,200.00"])
        assert detect_currency_pattern(series) is True

    def test_detects_yen_prefix(self):
        series = pd.Series(["¥150000"])
        assert detect_currency_pattern(series) is True

    def test_detects_usd_prefix(self):
        series = pd.Series(["USD 1500.00"])
        assert detect_currency_pattern(series) is True

    def test_detects_idr_prefix(self):
        series = pd.Series(["IDR 1500000"])
        assert detect_currency_pattern(series) is True

    def test_detects_eur_prefix(self):
        series = pd.Series(["EUR 1500.00"])
        assert detect_currency_pattern(series) is True

    def test_detects_gbp_prefix(self):
        series = pd.Series(["GBP 1200.00"])
        assert detect_currency_pattern(series) is True

    def test_detects_jpy_prefix(self):
        series = pd.Series(["JPY 150000"])
        assert detect_currency_pattern(series) is True

    def test_detects_usd_suffix(self):
        series = pd.Series(["1500.00 USD"])
        assert detect_currency_pattern(series) is True

    def test_detects_idr_suffix(self):
        series = pd.Series(["1500000 IDR"])
        assert detect_currency_pattern(series) is True

    def test_detects_mixed_series_with_one_currency(self):
        """Returns True if at least one value matches."""
        series = pd.Series(["hello", "world", "Rp 5000"])
        assert detect_currency_pattern(series) is True

    def test_returns_false_for_non_object_dtype_int(self):
        """Integer series should never be detected as currency."""
        series = pd.Series([1000, 2000, 3000])
        assert detect_currency_pattern(series) is False

    def test_returns_false_for_non_object_dtype_float(self):
        """Float series should never be detected as currency."""
        series = pd.Series([1.5, 2.5, 3.5])
        assert detect_currency_pattern(series) is False

    def test_returns_false_for_pure_numeric_strings(self):
        """String representations of plain numbers should not be detected."""
        series = pd.Series(["1000", "2000", "3000"])
        assert detect_currency_pattern(series) is False

    def test_returns_false_for_plain_text(self):
        series = pd.Series(["apple", "banana", "cherry"])
        assert detect_currency_pattern(series) is False

    def test_returns_false_for_empty_series(self):
        series = pd.Series([], dtype=object)
        assert detect_currency_pattern(series) is False

    def test_returns_false_for_all_null_series(self):
        series = pd.Series([None, None, None], dtype=object)
        assert detect_currency_pattern(series) is False

    def test_case_insensitive_usd(self):
        series = pd.Series(["usd 1500"])
        assert detect_currency_pattern(series) is True

    def test_case_insensitive_idr(self):
        series = pd.Series(["idr 1500000"])
        assert detect_currency_pattern(series) is True

    # Property 10: pure numeric series must NOT be detected as currency
    def test_property10_integer_list(self):
        """Property 10: Pure integer series → False."""
        series = pd.Series([1, 2, 3, 100, 999])
        assert detect_currency_pattern(series) is False

    def test_property10_float_list(self):
        """Property 10: Pure float series → False."""
        series = pd.Series([1.0, 2.5, 100.0, 999.99])
        assert detect_currency_pattern(series) is False

    def test_property10_numeric_string_list(self):
        """Property 10: Numeric strings without symbols → False."""
        series = pd.Series(["1000", "2000.50", "3000"])
        assert detect_currency_pattern(series) is False


# ---------------------------------------------------------------------------
# clean_currency_column — Indonesian format
# ---------------------------------------------------------------------------


class TestCleanCurrencyColumnIndonesian:
    """Tests for Indonesian number format (dot=thousands, comma=decimal)."""

    def test_basic_indonesian_format(self):
        """'Rp 1.500.000,50' → 1500000.5"""
        series = pd.Series(["Rp 1.500.000,50"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert result.dtype == "float64"
        assert math.isclose(result.iloc[0], 1_500_000.50)

    def test_indonesian_format_no_decimal(self):
        """'Rp 1.500.000' → 1500000.0"""
        series = pd.Series(["Rp 1.500.000"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_500_000.0)

    def test_indonesian_format_multiple_values(self):
        series = pd.Series(["Rp 1.000.000,00", "Rp 2.500.000,75", "Rp 500.000,00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_000_000.0)
        assert math.isclose(result.iloc[1], 2_500_000.75)
        assert math.isclose(result.iloc[2], 500_000.0)

    def test_idr_prefix_indonesian(self):
        series = pd.Series(["IDR 1.500.000,50"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_500_000.50)

    def test_euro_format_dot_thousands_comma_decimal(self):
        """€1.500,50 → 1500.5 (European format same as Indonesian)"""
        series = pd.Series(["€1.500,50"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_500.50)


# ---------------------------------------------------------------------------
# clean_currency_column — US format
# ---------------------------------------------------------------------------


class TestCleanCurrencyColumnUS:
    """Tests for US number format (comma=thousands, dot=decimal)."""

    def test_basic_us_format(self):
        """'$1,500.00' → 1500.0"""
        series = pd.Series(["$1,500.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert result.dtype == "float64"
        assert math.isclose(result.iloc[0], 1_500.0)

    def test_us_format_large_number(self):
        """'$1,500,000.99' → 1500000.99"""
        series = pd.Series(["$1,500,000.99"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_500_000.99)

    def test_us_format_no_thousands(self):
        """'$500.00' → 500.0"""
        series = pd.Series(["$500.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 500.0)

    def test_us_format_multiple_values(self):
        series = pd.Series(["$1,000.00", "$2,500.75", "$500.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_000.0)
        assert math.isclose(result.iloc[1], 2_500.75)
        assert math.isclose(result.iloc[2], 500.0)

    def test_usd_prefix_us_format(self):
        series = pd.Series(["USD 1,500.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_500.0)

    def test_gbp_prefix_us_format(self):
        series = pd.Series(["GBP 1,200.50"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_200.50)

    def test_jpy_prefix_no_decimal(self):
        series = pd.Series(["JPY 150000"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 150_000.0)


# ---------------------------------------------------------------------------
# clean_currency_column — NaN handling
# ---------------------------------------------------------------------------


class TestCleanCurrencyColumnNaN:
    """Tests for NaN counting and handling of unconvertible values."""

    def test_unconvertible_value_produces_nan(self):
        """Values that cannot be parsed should become NaN."""
        series = pd.Series(["$abc", "$1,000.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 1
        assert math.isnan(result.iloc[0])
        assert math.isclose(result.iloc[1], 1_000.0)

    def test_multiple_unconvertible_values(self):
        series = pd.Series(["$abc", "$xyz", "$1,000.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 2

    def test_original_nan_not_counted(self):
        """Pre-existing NaN values should not be counted in nan_count."""
        series = pd.Series(["$1,000.00", None, "$2,000.00"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0
        assert math.isclose(result.iloc[0], 1_000.0)
        assert math.isnan(result.iloc[1])
        assert math.isclose(result.iloc[2], 2_000.0)

    def test_all_valid_values_zero_nan_count(self):
        series = pd.Series(["Rp 1.000.000", "Rp 2.000.000"])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 0

    def test_result_dtype_is_float64(self):
        """Result must always be float64 regardless of input."""
        series = pd.Series(["$100.00", "$200.00"])
        result, _ = clean_currency_column(series)
        assert result.dtype == "float64"

    def test_empty_string_produces_nan(self):
        series = pd.Series(["$1,000.00", ""])
        result, nan_count = clean_currency_column(series)
        assert nan_count == 1
        assert math.isnan(result.iloc[1])
