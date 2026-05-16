"""
core/gemini_client.py — Gemini AI client for generating Python analysis code.

Manages communication with the Google Gemini AI API (gemini-2.5-flash model).
Builds a structured system prompt, sends user prompts, and extracts executable
Python code blocks from the model's response.
"""

import os
import re
from typing import Optional

import google.api_core.exceptions
import google.generativeai as genai


# ---------------------------------------------------------------------------
# Resampling frequency reference map (included in system prompt)
# ---------------------------------------------------------------------------

RESAMPLE_FREQ_MAP: dict[str, str] = {
    # Mingguan / Weekly
    "minggu": "W",
    "weekly": "W",
    "per minggu": "W-MON",
    # Bulanan / Monthly
    "bulan": "MS",
    "monthly": "MS",
    "per bulan": "MS",
    "month end": "ME",
    # Kuartalan / Quarterly
    "kuartal": "QS",
    "quarterly": "QS",
    "per kuartal": "QS",
    "quarter end": "QE",
    # Tahunan / Yearly
    "tahun": "YS",
    "yearly": "YS",
    "annual": "YS",
    "per tahun": "YS",
    "year end": "YE",
}


# ---------------------------------------------------------------------------
# Task 7 — GeminiClient class
# ---------------------------------------------------------------------------


class GeminiClient:
    """Client for interacting with the Google Gemini AI API.

    Generates executable Python code for data analysis and visualisation
    tasks based on a user prompt and the schema of the active DataFrame.

    Parameters
    ----------
    api_key : str, optional
        Gemini API key. If an empty string is provided (or the argument is
        omitted), the client falls back to the ``GEMINI_API_KEY`` environment
        variable.

    Attributes
    ----------
    model : google.generativeai.GenerativeModel
        The configured Gemini generative model instance.
    """

    def __init__(self, api_key: str = "") -> None:
        """Initialise the Gemini client.

        Task 7.1 — Configure ``google.generativeai`` with the provided API key,
        falling back to the ``GEMINI_API_KEY`` environment variable when the
        supplied key is empty.

        Parameters
        ----------
        api_key : str
            Gemini API key. Pass an empty string to use the environment
            variable ``GEMINI_API_KEY`` as a fallback.

        Requirements: 11.3, 11.4
        """
        resolved_key: str = api_key or os.environ.get("GEMINI_API_KEY", "")
        genai.configure(api_key=resolved_key)
        self.model: genai.GenerativeModel = genai.GenerativeModel("gemini-2.5-flash")

    # ------------------------------------------------------------------
    # Task 7.2 — System prompt builder
    # ------------------------------------------------------------------

    def _build_system_prompt(self, df_schema: dict) -> str:
        """Build the system prompt that instructs Gemini how to respond.

        The prompt is written in Indonesian and includes:
        - Role description and task definition
        - Mandatory coding rules (variable names, ``reset_index()``,
          ``drop(inplace=False)``, banned imports, etc.)
        - The active DataFrame schema as context
        - The ``RESAMPLE_FREQ_MAP`` as a resampling frequency reference

        Parameters
        ----------
        df_schema : dict
            Schema of the active DataFrame, typically produced by::

                {
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "shape": df.shape,
                    "sample": df.head(3).to_dict(orient="records"),
                }

        Returns
        -------
        str
            Fully rendered system prompt string.

        Requirements: 5.3, 12.12
        """
        resample_map_repr: str = "\n".join(
            f'    "{k}": "{v}",' for k, v in RESAMPLE_FREQ_MAP.items()
        )

        prompt: str = f"""Kamu adalah asisten analisis data Python yang ahli. Kamu akan diberikan skema DataFrame (nama kolom dan tipe data) dan instruksi dari pengguna.

TUGAS KAMU:
Hasilkan HANYA kode Python yang valid dan dapat dieksekusi. Jangan tambahkan penjelasan di luar blok kode.

ATURAN WAJIB:
1. DataFrame aktif tersedia sebagai variabel `df` (pandas DataFrame).
2. Untuk transformasi DataFrame SAJA (tanpa grafik): simpan hasil ke variabel `df` (overwrite).
3. Untuk grafik: WAJIB simpan objek Figure ke variabel bernama `fig` (HARUS persis `fig`, bukan nama lain). Gunakan Matplotlib atau Plotly.
4. PENTING — Jika instruksi meminta GRAFIK/CHART/VISUALISASI: JANGAN overwrite variabel `df`. Gunakan variabel sementara seperti `df_plot` atau `df_agg` untuk agregasi, lalu buat grafik dari variabel sementara tersebut dan simpan ke `fig`. Contoh pola yang BENAR:
   ```python
   df_agg = df.groupby('kategori')['sales'].sum().reset_index()
   fig = px.bar(df_agg, x='kategori', y='sales', title='Total Sales per Kategori')
   ```
   Contoh pola yang SALAH (jangan lakukan ini saat membuat grafik):
   ```python
   df = df.groupby('kategori')['sales'].sum().reset_index()  # SALAH: overwrite df saat tujuannya grafik
   fig = px.bar(df, ...)
   ```
5. Untuk output teks: gunakan `print()`.
6. Setelah operasi resample/groupby time-series, SELALU panggil `.reset_index()` agar kolom datetime menjadi kolom eksplisit.
7. Gunakan `df.drop(columns=[...], inplace=False)` untuk menghapus kolom, simpan ke `df`.
8. Jangan gunakan `input()`, `open()`, akses file system, atau import modul berbahaya.
9. Import library yang diperlukan di dalam blok kode (pandas, numpy, matplotlib, plotly, seaborn, dll.). Library yang tersedia di sandbox: `pd`, `np`, `plt`, `px`, `go`, `sns`, `df`. JANGAN gunakan library lain seperti `bokeh`, `altair`, `scipy`, `sklearn` karena tidak tersedia.
10. SEBELUM melakukan operasi numerik (sum, mean, plot, groupby agregasi, dll.) pada kolom bertipe `object`, SELALU bersihkan dulu dengan: `df['kolom'] = pd.to_numeric(df['kolom'].astype(str).str.replace(',', ''), errors='coerce')`. Ini menangani format angka dengan koma ribuan seperti "1,706.18".
11. Jika kolom yang akan digunakan untuk grafik atau kalkulasi bertipe `object` (bukan `int64`/`float64`), lakukan konversi numerik terlebih dahulu sebelum digunakan.
12. Untuk heatmap, gunakan `seaborn` (`sns.heatmap()`) dengan Matplotlib figure, atau gunakan `plotly.express.imshow()`. Simpan figure ke variabel `fig`.
13. Untuk grafik TIME-SERIES (area chart, line chart, bar chart per waktu), WAJIB ikuti pola ini PERSIS:
    LANGKAH 1 — Siapkan data (gunakan nama kolom SESUAI skema df di atas):
    ```python
    df_plot = df.copy()
    # Konversi kolom tanggal ke datetime (ganti 'NamaKolomTanggal' dengan nama kolom aktual dari skema)
    df_plot['NamaKolomTanggal'] = pd.to_datetime(df_plot['NamaKolomTanggal'], errors='coerce')
    # Hapus baris dengan tanggal tidak valid
    df_plot = df_plot.dropna(subset=['NamaKolomTanggal'])
    # Konversi kolom numerik (ganti dengan nama kolom aktual)
    for col in ['NamaKolomNumerik1', 'NamaKolomNumerik2']:
        df_plot[col] = pd.to_numeric(df_plot[col].astype(str).str.replace(',', ''), errors='coerce')
    ```
    LANGKAH 2 — Filter rentang tahun:
    ```python
    # Untuk rentang tahun (misal 2019-2021):
    df_plot = df_plot[df_plot['NamaKolomTanggal'].dt.year.between(2019, 2021)]
    # Untuk satu tahun (misal 2020):
    df_plot = df_plot[df_plot['NamaKolomTanggal'].dt.year == 2020]
    ```
    LANGKAH 3 — Cek data tidak kosong:
    ```python
    if df_plot.empty:
        print(f"Tidak ada data. Rentang tanggal tersedia: {{df['NamaKolomTanggal'].min()}} - {{df['NamaKolomTanggal'].max()}}")
    else:
    ```
    LANGKAH 4 — Resample dan buat label (DALAM blok else):
    ```python
        # Set index dan resample
        df_ts = df_plot.set_index('NamaKolomTanggal')[['NamaKolomNumerik1', 'NamaKolomNumerik2']].resample('MS').sum().reset_index()
        # Buat label string untuk sumbu x (WAJIB string, bukan integer/datetime)
        df_ts['label'] = df_ts['NamaKolomTanggal'].dt.strftime('%b %Y')  # per bulan
        # ATAU per tahun: df_ts['label'] = df_ts['NamaKolomTanggal'].dt.strftime('%Y')
        # ATAU per kuartal: df_ts['label'] = df_ts['NamaKolomTanggal'].dt.to_period('Q').astype(str)
        fig = px.area(df_ts, x='label', y=['NamaKolomNumerik1', 'NamaKolomNumerik2'],
                      title='Judul Grafik')
    ```
14. JANGAN gunakan groupby per bulan jika user meminta per kuartal. Pastikan granularitas agregasi sesuai permintaan user.
15. WAJIB konversi kolom tanggal ke datetime64 SEBELUM filter atau resample. Gunakan variabel sementara `df_plot = df.copy()` agar `df` asli tidak berubah.
16. FORMAT SUMBU X DATETIME — ATURAN KRITIS:
    - SELALU gunakan kolom label STRING untuk sumbu x, JANGAN gunakan kolom datetime atau integer langsung.
    - Per tahun: `dt.strftime('%Y')` → "2019", "2020", "2021"
    - Per bulan: `dt.strftime('%b %Y')` → "Jan 2019", "Feb 2019"
    - Per kuartal: `dt.to_period('Q').astype(str)` → "2019Q1", "2019Q2"
    - DILARANG: `x=df_ts['year']` atau `x=df_ts['col'].dt.year` → akan menghasilkan "2,019" bukan "2019"
17. Untuk grafik area chart multi-series, gunakan `px.area(df_ts, x='label', y=['kolom1', 'kolom2'])`. Pastikan kolom numerik sudah bersih dari NaN sebelum plotting.

SKEMA DATAFRAME AKTIF:
{df_schema}

REFERENSI FREKUENSI RESAMPLING (RESAMPLE_FREQ_MAP):
{{
{resample_map_repr}
}}

FORMAT OUTPUT:
```python
# kode Python di sini
```"""

        return prompt

    # ------------------------------------------------------------------
    # Task 7.3 — Code block extractor
    # ------------------------------------------------------------------

    def _extract_code_block(self, response_text: str) -> str:
        """Extract the Python code block from a Gemini markdown response.

        Looks for a fenced code block of the form::

            ```python
            # code here
            ```

        and returns only the code content inside, without the markdown
        fence characters.

        Parameters
        ----------
        response_text : str
            Raw text response from the Gemini API.

        Returns
        -------
        str
            The extracted Python code string, stripped of leading/trailing
            whitespace. Returns an empty string if no code block is found.

        Requirements: 5.4
        """
        pattern = re.compile(
            r"```python\s*\n(.*?)```",
            re.DOTALL,
        )
        match = pattern.search(response_text)
        if match:
            return match.group(1).strip()
        return ""

    # ------------------------------------------------------------------
    # Task 7.4 — Main code generation method
    # ------------------------------------------------------------------

    def generate_code(
        self,
        prompt: str,
        df_schema: dict,
    ) -> tuple[Optional[str], Optional[str]]:
        """Send a user prompt to Gemini and return the generated Python code.

        Combines the user prompt with a structured system prompt (built from
        ``df_schema``) and sends the request to the ``gemini-2.5-flash`` model.
        The code block is extracted from the response and returned.

        Parameters
        ----------
        prompt : str
            Natural-language instruction from the user (e.g. "Buat grafik
            batang jumlah penjualan per bulan").
        df_schema : dict
            Schema of the active DataFrame passed to ``_build_system_prompt()``.

        Returns
        -------
        tuple[str | None, str | None]
            ``(code, None)`` on success, where *code* is the extracted Python
            source string.
            ``(None, error_message)`` on failure, where *error_message* is a
            human-readable Indonesian error description.

        Error handling
        --------------
        - ``google.api_core.exceptions.InvalidArgument`` → invalid API key
        - ``google.api_core.exceptions.ResourceExhausted`` → quota exceeded
        - Any other ``Exception`` → generic communication error

        Requirements: 5.2, 5.3
        """
        system_prompt: str = self._build_system_prompt(df_schema)
        full_prompt: str = f"{system_prompt}\n\nINSTRUKSI PENGGUNA:\n{prompt}"

        try:
            response = self.model.generate_content(full_prompt)
            code: str = self._extract_code_block(response.text)
            if not code:
                return None, "AI tidak menghasilkan kode Python yang valid."
            return code, None

        except google.api_core.exceptions.InvalidArgument:
            return None, "API Key tidak valid. Periksa kembali Gemini API Key Anda."

        except google.api_core.exceptions.ResourceExhausted:
            return None, "Kuota API habis. Coba lagi nanti."

        except Exception as e:  # noqa: BLE001
            return None, f"Error komunikasi dengan Gemini AI: {str(e)}"
