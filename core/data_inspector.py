"""
core/data_inspector.py — Data inspection and summary utilities.

Provides functions to compute descriptive statistics, detect outliers,
identify currency-formatted columns, and render a comprehensive data
summary to the Streamlit UI.
"""

import pandas as pd
import streamlit as st

from core import currency_cleaner


def get_outliers(df: pd.DataFrame) -> dict[str, list]:
    """Detect outliers in numeric columns using the IQR method.

    For each numeric column, computes Q1, Q3, and IQR, then collects
    all values that fall outside the range [Q1 - 1.5×IQR, Q3 + 1.5×IQR].

    Parameters
    ----------
    df:
        The DataFrame to inspect.

    Returns
    -------
    dict[str, list]
        A mapping of column name → list of outlier values.
        Only columns that actually contain outliers are included.

    Requirements: 4.9
    """
    outliers: dict[str, list] = {}
    for col in df.select_dtypes(include="number").columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        mask = (df[col] < lower) | (df[col] > upper)
        if mask.any():
            outliers[col] = df[col][mask].tolist()
    return outliers


def detect_currency_columns(df: pd.DataFrame) -> list[str]:
    """Identify columns that contain currency-formatted values.

    Iterates over all ``object``-dtype columns and delegates detection
    to :func:`currency_cleaner.detect_currency_pattern`.

    Parameters
    ----------
    df:
        The DataFrame to inspect.

    Returns
    -------
    list[str]
        Names of columns detected as Currency_Column.

    Requirements: 13.1, 13.2
    """
    currency_cols: list[str] = []
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if currency_cleaner.detect_currency_pattern(df[col]):
            currency_cols.append(col)
    return currency_cols


def get_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for numeric columns.

    Wraps ``DataFrame.describe()`` to return count, mean, std, min,
    25th percentile, median, 75th percentile, and max for every numeric
    column in *df*.

    Parameters
    ----------
    df:
        The DataFrame to describe.

    Returns
    -------
    pd.DataFrame
        Descriptive statistics table (columns = numeric columns of *df*,
        rows = statistics).

    Requirements: 4.8
    """
    return df.describe()


def render_summary(df: pd.DataFrame, filename: str) -> None:
    """Render a comprehensive data summary to the Streamlit UI.

    Displays the following sections in order:

    1. Active filename
    2. Number of rows and columns
    3. Preview of the first 5 rows
    4. Data type of each column
    5. Number of null values per column
    6. Number of duplicate rows
    7. Descriptive statistics (numeric columns only)
    8. Outliers per numeric column, or an informative message when there
       are no numeric columns
    9. Detected Currency_Columns with example values

    Parameters
    ----------
    df:
        The active DataFrame to summarise.
    filename:
        The name of the uploaded file currently in session.

    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 13.2
    """
    # ------------------------------------------------------------------ #
    # 1. Active filename                                                   #
    # ------------------------------------------------------------------ #
    st.subheader("File Aktif")
    st.write(filename)

    # ------------------------------------------------------------------ #
    # 2. Shape — rows and columns                                          #
    # ------------------------------------------------------------------ #
    st.subheader("Dimensi Data")
    col_rows, col_cols = st.columns(2)
    col_rows.metric("Jumlah Baris", df.shape[0])
    col_cols.metric("Jumlah Kolom", df.shape[1])

    # ------------------------------------------------------------------ #
    # 3. Preview — first 5 rows                                            #
    # ------------------------------------------------------------------ #
    st.subheader("Preview Data (5 Baris Pertama)")
    st.dataframe(df.head(5), width="stretch")

    # ------------------------------------------------------------------ #
    # 4. Data types per column                                             #
    # ------------------------------------------------------------------ #
    st.subheader("Tipe Data Kolom")
    dtype_df = pd.DataFrame(
        {"Kolom": df.dtypes.index, "Tipe Data": df.dtypes.values.astype(str)}
    ).reset_index(drop=True)
    st.dataframe(dtype_df, width="stretch")

    # ------------------------------------------------------------------ #
    # 5. Null values per column                                            #
    # ------------------------------------------------------------------ #
    st.subheader("Nilai Null per Kolom")
    null_counts = df.isnull().sum()
    null_df = pd.DataFrame(
        {"Kolom": null_counts.index, "Jumlah Null": null_counts.values}
    ).reset_index(drop=True)
    st.dataframe(null_df, width="stretch")

    # ------------------------------------------------------------------ #
    # 6. Duplicate rows                                                    #
    # ------------------------------------------------------------------ #
    st.subheader("Baris Duplikat")
    n_duplicates = int(df.duplicated().sum())
    st.write(f"Jumlah baris duplikat: **{n_duplicates}**")

    # ------------------------------------------------------------------ #
    # 7. Descriptive statistics                                            #
    # ------------------------------------------------------------------ #
    st.subheader("Statistik Deskriptif")
    numeric_cols = df.select_dtypes(include="number")
    if not numeric_cols.empty:
        stats_df = get_descriptive_stats(df)
        st.dataframe(stats_df, width="stretch")
    else:
        st.info("Tidak ada kolom numerik - statistik deskriptif tidak tersedia.")

    # ------------------------------------------------------------------ #
    # 8. Outliers                                                          #
    # ------------------------------------------------------------------ #
    st.subheader("Outlier (Metode IQR)")
    if numeric_cols.empty:
        st.info(
            "Deteksi outlier tidak tersedia karena DataFrame tidak memiliki "
            "kolom numerik."
        )
    else:
        outliers = get_outliers(df)
        if outliers:
            for col, values in outliers.items():
                with st.expander(f"Kolom: **{col}** — {len(values)} outlier"):
                    st.write(values)
        else:
            st.write("Tidak ditemukan outlier pada kolom numerik.")

    # ------------------------------------------------------------------ #
    # 9. Currency columns                                                  #
    # ------------------------------------------------------------------ #
    st.subheader("Kolom Mata Uang Terdeteksi")
    currency_cols = detect_currency_columns(df)
    if currency_cols:
        for col in currency_cols:
            examples = df[col].dropna().head(3).tolist()
            st.write(f"**{col}** — Contoh nilai: {examples}")
    else:
        st.info("Tidak ada kolom mata uang yang terdeteksi.")
