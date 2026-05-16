"""
Unit tests for core/data_inspector.py

Tests cover:
- get_outliers() with DataFrame that has clear outliers
- get_outliers() with DataFrame without numeric columns
- detect_currency_columns() with various currency formats

Streamlit's st.* calls are mocked throughout since they require a Streamlit context.

Requirements: 4.9, 4.10, 13.1
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from core.data_inspector import detect_currency_columns, get_outliers


# ---------------------------------------------------------------------------
# get_outliers — IQR-based outlier detection
# ---------------------------------------------------------------------------


class TestGetOutliers:
    """Tests for get_outliers()."""

    def test_detects_clear_outliers(self):
        """A value far outside the IQR range should be detected as an outlier."""
        # Values 1-10 are tightly clustered; 1000 is a clear outlier
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1000]})
        result = get_outliers(df)
        assert "value" in result
        assert 1000 in result["value"]

    def test_detects_low_outlier(self):
        """A value far below Q1 - 1.5*IQR should be detected."""
        df = pd.DataFrame({"value": [-1000, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        result = get_outliers(df)
        assert "value" in result
        assert -1000 in result["value"]

    def test_detects_outliers_in_multiple_columns(self):
        """Outliers in multiple numeric columns should all be reported."""
        df = pd.DataFrame(
            {
                "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1000],
                "b": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, -9999],
            }
        )
        result = get_outliers(df)
        assert "a" in result
        assert "b" in result
        assert 1000 in result["a"]
        assert -9999 in result["b"]

    def test_no_outliers_returns_empty_dict(self):
        """A normally distributed tight cluster should produce no outliers."""
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        result = get_outliers(df)
        # May or may not have outliers depending on IQR; just verify structure
        assert isinstance(result, dict)
        # For this tight range, no outliers expected
        assert "value" not in result

    def test_returns_empty_dict_for_no_numeric_columns(self):
        """DataFrame with only object columns should return an empty dict."""
        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "city": ["Jakarta", "Bandung", "Surabaya"]})
        result = get_outliers(df)
        assert result == {}

    def test_returns_empty_dict_for_empty_dataframe(self):
        """Empty DataFrame should return an empty dict."""
        df = pd.DataFrame()
        result = get_outliers(df)
        assert result == {}

    def test_outlier_values_are_actual_dataframe_values(self):
        """Reported outlier values must be actual values from the DataFrame."""
        df = pd.DataFrame({"score": [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 200]})
        result = get_outliers(df)
        if "score" in result:
            for val in result["score"]:
                assert val in df["score"].values

    def test_outlier_values_satisfy_iqr_condition(self):
        """Every reported outlier must be outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]."""
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1000]})
        result = get_outliers(df)
        for col, values in result.items():
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            for v in values:
                assert v < lower or v > upper, (
                    f"Value {v} in column '{col}' is not outside [{lower}, {upper}]"
                )

    def test_returns_dict_type(self):
        """Return type must always be a dict."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        result = get_outliers(df)
        assert isinstance(result, dict)

    def test_column_not_in_result_when_no_outliers(self):
        """Columns without outliers should not appear in the result dict."""
        # All values identical → IQR = 0, no outliers
        df = pd.DataFrame({"constant": [5, 5, 5, 5, 5]})
        result = get_outliers(df)
        assert "constant" not in result

    def test_mixed_columns_only_numeric_inspected(self):
        """Only numeric columns should be inspected; object columns ignored."""
        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank", "Grace", "Hank", "Iris", "Jack", "Outlier"],
                "value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1000],
            }
        )
        result = get_outliers(df)
        assert "name" not in result
        assert "value" in result


# ---------------------------------------------------------------------------
# detect_currency_columns — currency column detection
# ---------------------------------------------------------------------------


class TestDetectCurrencyColumns:
    """Tests for detect_currency_columns()."""

    def test_detects_rp_column(self):
        """Column with Rp-prefixed values should be detected."""
        df = pd.DataFrame({"harga": ["Rp 1.500.000", "Rp 2.000.000", "Rp 500.000"]})
        result = detect_currency_columns(df)
        assert "harga" in result

    def test_detects_dollar_column(self):
        """Column with $-prefixed values should be detected."""
        df = pd.DataFrame({"price": ["$1,500.00", "$200.00", "$3,000.00"]})
        result = detect_currency_columns(df)
        assert "price" in result

    def test_detects_euro_column(self):
        """Column with €-prefixed values should be detected."""
        df = pd.DataFrame({"preis": ["€1.500,50", "€200,00"]})
        result = detect_currency_columns(df)
        assert "preis" in result

    def test_detects_usd_prefix_column(self):
        """Column with USD literal prefix should be detected."""
        df = pd.DataFrame({"amount": ["USD 1500.00", "USD 200.00"]})
        result = detect_currency_columns(df)
        assert "amount" in result

    def test_detects_idr_prefix_column(self):
        """Column with IDR literal prefix should be detected."""
        df = pd.DataFrame({"nilai": ["IDR 1500000", "IDR 200000"]})
        result = detect_currency_columns(df)
        assert "nilai" in result

    def test_detects_multiple_currency_columns(self):
        """Multiple currency columns should all be detected."""
        df = pd.DataFrame(
            {
                "harga_rp": ["Rp 1.000.000", "Rp 2.000.000"],
                "price_usd": ["$1,000.00", "$2,000.00"],
                "name": ["Product A", "Product B"],
            }
        )
        result = detect_currency_columns(df)
        assert "harga_rp" in result
        assert "price_usd" in result
        assert "name" not in result

    def test_does_not_detect_plain_text_column(self):
        """Columns with plain text should not be detected as currency."""
        df = pd.DataFrame({"description": ["apple", "banana", "cherry"]})
        result = detect_currency_columns(df)
        assert "description" not in result

    def test_does_not_detect_numeric_column(self):
        """Numeric (int/float) columns should not be detected as currency."""
        df = pd.DataFrame({"amount": [1000, 2000, 3000]})
        result = detect_currency_columns(df)
        assert "amount" not in result

    def test_does_not_detect_pure_numeric_string_column(self):
        """Columns with plain numeric strings should not be detected."""
        df = pd.DataFrame({"value": ["1000", "2000", "3000"]})
        result = detect_currency_columns(df)
        assert "value" not in result

    def test_returns_empty_list_for_no_currency_columns(self):
        """DataFrame with no currency columns should return empty list."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        result = detect_currency_columns(df)
        assert result == []

    def test_returns_list_type(self):
        """Return type must always be a list."""
        df = pd.DataFrame({"x": ["hello", "world"]})
        result = detect_currency_columns(df)
        assert isinstance(result, list)

    def test_returns_empty_list_for_empty_dataframe(self):
        """Empty DataFrame should return empty list."""
        df = pd.DataFrame()
        result = detect_currency_columns(df)
        assert result == []

    def test_detects_suffix_currency_column(self):
        """Column with currency suffix (e.g. '1500 USD') should be detected."""
        df = pd.DataFrame({"amount": ["1500 USD", "2000 USD"]})
        result = detect_currency_columns(df)
        assert "amount" in result

    def test_detects_pound_column(self):
        """Column with £-prefixed values should be detected."""
        df = pd.DataFrame({"price": ["£1,200.00", "£500.00"]})
        result = detect_currency_columns(df)
        assert "price" in result

    def test_detects_yen_column(self):
        """Column with ¥-prefixed values should be detected."""
        df = pd.DataFrame({"price": ["¥150000", "¥200000"]})
        result = detect_currency_columns(df)
        assert "price" in result
