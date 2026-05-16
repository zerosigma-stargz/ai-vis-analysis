"""
core/file_parser.py — Multi-format file parsing utilities.

Converts uploaded files (CSV, TSV, JSON, JSONL, PDF, Parquet) into
pandas DataFrames. Routing is handled by the public ``parse()`` function
which dispatches to a format-specific private parser based on the file
extension.
"""

from __future__ import annotations

import io
import json
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile


# ---------------------------------------------------------------------------
# Private parser functions — one per supported format
# ---------------------------------------------------------------------------


def _parse_csv(file: io.IOBase) -> pd.DataFrame:
    """Parse a CSV file into a DataFrame.

    Parameters
    ----------
    file:
        A file-like object containing CSV data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame.

    Requirements: 3.1
    """
    return pd.read_csv(file)


def _parse_tsv(file: io.IOBase) -> pd.DataFrame:
    """Parse a TSV (tab-separated values) file into a DataFrame.

    Parameters
    ----------
    file:
        A file-like object containing TSV data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame.

    Requirements: 3.2
    """
    return pd.read_csv(file, sep="\t")


def _parse_json(file: io.IOBase) -> pd.DataFrame:
    """Parse a JSON file into a DataFrame.

    Parameters
    ----------
    file:
        A file-like object containing JSON data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame.

    Requirements: 3.3
    """
    return pd.read_json(file)


def _parse_jsonl(file: io.IOBase) -> pd.DataFrame:
    """Parse a JSON Lines file into a DataFrame.

    Each line in the file is expected to be a valid JSON object. Lines that
    are empty or contain only whitespace are skipped.

    Parameters
    ----------
    file:
        A file-like object containing JSON Lines data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame built from the list of JSON objects.

    Raises
    ------
    ValueError
        If no valid JSON objects are found in the file.

    Requirements: 3.4
    """
    records: list[dict] = []
    for raw_line in file:
        # Handle both bytes and str lines
        if isinstance(raw_line, bytes):
            line = raw_line.decode("utf-8")
        else:
            line = raw_line
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))

    if not records:
        raise ValueError("File JSONL tidak mengandung baris JSON yang valid.")

    return pd.DataFrame(records)


def _parse_parquet(file: io.IOBase) -> pd.DataFrame:
    """Parse a Parquet file into a DataFrame.

    Parameters
    ----------
    file:
        A file-like object containing Parquet data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame.

    Requirements: 3.6
    """
    return pd.read_parquet(file)


def _parse_xlsx(file: io.IOBase) -> pd.DataFrame:
    """Parse an Excel (.xlsx) file into a DataFrame.

    Parameters
    ----------
    file:
        A file-like object containing XLSX data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame from the first sheet.

    Requirements: 3.9
    """
    return pd.read_excel(file, engine="openpyxl")


def _parse_xls(file: io.IOBase) -> pd.DataFrame:
    """Parse a legacy Excel (.xls) file into a DataFrame.

    Parameters
    ----------
    file:
        A file-like object containing XLS data.

    Returns
    -------
    pd.DataFrame
        The parsed DataFrame from the first sheet.

    Requirements: 3.9
    """
    return pd.read_excel(file, engine="xlrd")


def _parse_pdf(file: "UploadedFile") -> pd.DataFrame:
    """Parse a PDF file by extracting the first table found.

    Extraction strategy:
    1. Try ``pdfplumber`` for table extraction.
    2. Fall back to ``camelot-py`` if pdfplumber finds no tables.
    3. Return the first table found as a DataFrame.

    Parameters
    ----------
    file:
        A Streamlit ``UploadedFile`` object for the PDF.

    Returns
    -------
    pd.DataFrame
        The first table found in the PDF as a DataFrame.

    Raises
    ------
    ValueError
        If no table is found in the PDF by either library.

    Requirements: 3.5
    """
    import pdfplumber  # type: ignore[import]

    # --- Attempt 1: pdfplumber ---
    pdf_bytes = file.read()
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                raw_table = tables[0]
                # Use the first row as header if it looks like one
                if raw_table and raw_table[0]:
                    header = raw_table[0]
                    rows = raw_table[1:]
                    df = pd.DataFrame(rows, columns=header)
                    return df

    # --- Attempt 2: camelot-py (requires a file path) ---
    try:
        import camelot  # type: ignore[import]
    except ImportError as exc:
        raise ValueError(
            "Tidak ditemukan tabel dalam file PDF. "
            "Library 'camelot-py' tidak tersedia sebagai fallback."
        ) from exc

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        tables = camelot.read_pdf(tmp_path, pages="all")
        if tables and len(tables) > 0:
            return tables[0].df
    finally:
        import os

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    raise ValueError(
        "Tidak ditemukan tabel dalam file PDF. "
        "Pastikan file PDF mengandung tabel yang dapat diekstrak."
    )


# ---------------------------------------------------------------------------
# Extension → parser mapping
# ---------------------------------------------------------------------------

_PARSERS = {
    ".csv": _parse_csv,
    ".tsv": _parse_tsv,
    ".json": _parse_json,
    ".jsonl": _parse_jsonl,
    ".parquet": _parse_parquet,
    ".pdf": _parse_pdf,
    ".xlsx": _parse_xlsx,
    ".xls": _parse_xls,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse(uploaded_file: "UploadedFile") -> pd.DataFrame | None:
    """Parse an uploaded file into a pandas DataFrame.

    Routes the file to the appropriate parser based on its extension, then
    validates that the resulting DataFrame is non-empty. Any error during
    parsing is caught, displayed via ``st.error()``, and ``None`` is returned
    so the caller can handle the failure gracefully without crashing.

    Parameters
    ----------
    uploaded_file:
        A Streamlit ``UploadedFile`` object. Must have a ``.name`` attribute
        and support ``.read()`` / file-like access.

    Returns
    -------
    pd.DataFrame | None
        The parsed DataFrame on success, or ``None`` if parsing failed.

    Requirements: 3.7, 3.8
    """
    filename: str = uploaded_file.name
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    parser = _PARSERS.get(ext)
    if parser is None:
        st.error(
            f"❌ Format file tidak didukung: '{ext}'. "
            f"Format yang didukung: {', '.join(_PARSERS.keys())}."
        )
        return None

    try:
        df: pd.DataFrame = parser(uploaded_file)

        if df.empty:
            raise ValueError(
                f"File '{filename}' berhasil dibaca tetapi tidak mengandung data."
            )

        return df

    except ValueError as exc:
        st.error(f"❌ Gagal memproses file '{filename}': {exc}")
        return None
    except Exception as exc:  # noqa: BLE001
        st.error(
            f"❌ Gagal memproses file '{filename}': {exc}"
        )
        return None
