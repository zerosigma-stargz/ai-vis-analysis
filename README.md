# 🤖 AI Assistance Analisis & Visualisasi Chart Grafik Data

Aplikasi web berbasis **Python** dan **Streamlit** yang memungkinkan pengguna menganalisis data dan membuat visualisasi grafik secara otomatis hanya dengan mengunggah file dan mengetikkan instruksi dalam bahasa alami. Didukung oleh **Gemini 2.5 Flash** dari Google AI.

> **✨ Tampilan Modern dengan Gradient Ungu-Biru**  
> Interface yang elegan, user-friendly, dan cocok untuk berbagai kalangan profesional multi-disipliner — dari kesehatan, bisnis, sains, hingga teknologi.

---

## ✨ Fitur Utama

### 📂 Parsing Multi-Format
Unggah file data dalam berbagai format — aplikasi secara otomatis mengonversinya ke pandas DataFrame:

| Format | Ekstensi | Keterangan |
|--------|----------|------------|
| CSV | `.csv` | Comma-separated values |
| TSV | `.tsv` | Tab-separated values |
| JSON | `.json` | JSON array atau object |
| JSON Lines | `.jsonl` | Satu JSON object per baris |
| PDF | `.pdf` | Ekstraksi tabel otomatis (pdfplumber + camelot) |
| Parquet | `.parquet` | Format kolumnar Apache Parquet |
| Excel | `.xlsx` / `.xls` | Sheet pertama diambil secara otomatis |

Ukuran file maksimal: **200 MB**

---

### 📊 Inspeksi Data Otomatis
Setelah file diunggah, aplikasi langsung menampilkan ringkasan lengkap tanpa perlu konfigurasi tambahan:

- Dimensi data (jumlah baris dan kolom)
- Preview 5 baris pertama
- Tipe data setiap kolom
- Jumlah nilai null per kolom
- Jumlah baris duplikat
- Statistik deskriptif (count, mean, std, min, 25%, 50%, 75%, max)
- Deteksi outlier menggunakan metode **IQR** (Q1 − 1.5×IQR hingga Q3 + 1.5×IQR)
- Deteksi kolom mata uang (Rp, $, €, £, ¥, USD, IDR, EUR, GBP, JPY)

---

### 💬 Chatbot AI — Transformasi DataFrame
Ketik instruksi dalam bahasa Indonesia atau Inggris di sidebar, dan Gemini AI akan menghasilkan kode Python yang langsung dieksekusi terhadap data Anda:

- Filter baris berdasarkan kondisi
- Seleksi dan penghapusan kolom
- Penambahan kolom baru (aritmetika, kondisi logika, ekstraksi datetime)
- Pengurutan dan agregasi data (`sum`, `mean`, `count`, `min`, `max`, `median`, `std`, `var`)
- Groupby dan pivot
- Konversi kolom mata uang ke `float64`
- Resampling time-series (mingguan, bulanan, kuartalan, tahunan)

---

### 📈 Visualisasi Grafik Otomatis
Minta AI untuk membuat grafik langsung dari data Anda:

- **Bar Chart** — perbandingan kategori
- **Line Chart** — tren waktu
- **Area Chart** — tren kumulatif multi-series
- **Scatter Plot** — korelasi antar variabel
- **Pie Chart** — distribusi proporsi
- **Box Plot** — distribusi dan outlier
- **Heatmap** — korelasi matriks

Grafik dirender menggunakan **Matplotlib** atau **Plotly** (interaktif).

---

### 🔍 Analisis Grafik Otomatis (Chart Insight)
Setiap grafik yang dihasilkan dilengkapi panel analisis otomatis dari Gemini AI:

| Panel | Isi |
|-------|-----|
| 🎯 **Tujuan Grafik** | Penjelasan 1–2 kalimat tentang tujuan spesifik grafik berdasarkan permintaan dan kolom yang digunakan |
| 📖 **Deskripsi Isi Grafik** | Deskripsi 2–3 kalimat tentang pola, tren, atau perbandingan yang terlihat |
| 💡 **Tips Insight** | 2–3 saran analisis lanjutan yang actionable dan spesifik terhadap data |

Insight dihasilkan dalam **bahasa Indonesia** dan fokus pada kolom/variabel yang benar-benar digunakan dalam permintaan pengguna.

---

### 🔒 Keamanan Eksekusi Kode
Kode Python yang dihasilkan AI dieksekusi dalam **sandbox terbatas**:

- Import modul berbahaya diblokir (`os`, `sys`, `subprocess`, `shutil`, `socket`)
- Timeout eksekusi 30 detik
- DataFrame asli tidak pernah dimutasi langsung (selalu menggunakan salinan)

---

## 🚀 Cara Menjalankan

### 1. Prasyarat

- Python **3.10** atau lebih baru
- Gemini API Key dari [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Clone dan Install Dependensi

```bash
git clone <url-repository>
cd chatbot-analisis-visualisasi-data

# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau
.venv\Scripts\activate     # Windows

# Install semua dependensi
pip install -r requirements.txt
```

### 3. Konfigurasi API Key

Buat file `.env` di root direktori proyek:

```bash
cp .env.example .env
```

Isi file `.env` dengan API Key Anda:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Alternatif:** API Key juga dapat dimasukkan langsung melalui sidebar aplikasi saat runtime, tanpa perlu file `.env`.

### 4. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.

**🎉 Selamat! Anda siap menganalisis data dengan AI.**

---

## 📁 Struktur Proyek

```
chatbot-analisis-visualisasi-data/
├── app.py                        # Entry point Streamlit
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py                # Sidebar: API key, prompt box, reset
│   ├── landing_page.py           # Halaman awal + file uploader
│   ├── data_page.py              # Halaman data + chat area
│   └── chat_area.py              # Render riwayat chat + Chart Insight
│
├── core/
│   ├── __init__.py
│   ├── file_parser.py            # Parser multi-format → DataFrame
│   ├── data_inspector.py         # Statistik, outlier, deteksi mata uang
│   ├── gemini_client.py          # Gemini AI: generate_code + generate_chart_insight
│   ├── code_executor.py          # Sandbox exec() dengan timeout
│   └── currency_cleaner.py       # Deteksi & konversi kolom mata uang
│
├── utils/
│   ├── __init__.py
│   └── chart_renderer.py         # Render Matplotlib/Plotly ke Streamlit
│
├── tests/
│   ├── unit/                     # Unit tests + property-based tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # File fixture untuk testing
│
├── .env.example                  # Template variabel lingkungan
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Stack Teknologi

| Kategori | Library | Versi |
|----------|---------|-------|
| Framework UI | Streamlit | 1.45.1 |
| Data Processing | pandas | 2.2.3 |
| Data Processing | numpy | 2.2.5 |
| Parquet Support | pyarrow | 20.0.0 |
| Excel Support | openpyxl | 3.1.5 |
| Excel Support (legacy) | xlrd | 2.0.1 |
| PDF Parsing | pdfplumber | 0.11.6 |
| PDF Parsing (fallback) | camelot-py[cv] | 0.11.0 |
| AI | google-generativeai | 0.8.5 |
| Visualisasi | matplotlib | 3.10.3 |
| Visualisasi | plotly | 6.1.1 |
| Visualisasi | seaborn | 0.13.2 |
| Environment | python-dotenv | 1.1.0 |
| Testing | pytest | 8.3.5 |
| Property Testing | hypothesis | 6.131.15 |

---

## 🧪 Menjalankan Tests

```bash
# Semua unit tests
pytest tests/unit/ -v

# Dengan coverage report
pytest tests/unit/ --cov=core --cov=utils --cov=components --cov-report=term-missing

# Integration tests (memerlukan file fixture)
pytest tests/integration/ -v

# Property-based tests dengan profil CI (100 contoh per test)
pytest tests/ -v
```

---

## 💡 Contoh Penggunaan

### Analisis Data Penjualan

1. Unggah file `penjualan.csv`
2. Aplikasi otomatis menampilkan statistik dan mendeteksi kolom mata uang
3. Ketik di prompt box:
   - `"Buat bar chart total penjualan per kategori produk"`
   - `"Tampilkan tren penjualan bulanan tahun 2023 sebagai line chart"`
   - `"Hitung rata-rata profit per region"`
   - `"Hapus kolom 'id' dan 'temp'"`
   - `"Konversi kolom 'harga' dari format Rp ke float"`

### Analisis Time-Series

1. Unggah file dengan kolom tanggal
2. Ketik:
   - `"Buat area chart total sales dan profit per bulan tahun 2022-2023"`
   - `"Tampilkan agregasi penjualan per kuartal sebagai bar chart"`
   - `"Resample data ke mingguan dan tampilkan tren"`

---

## ⚙️ Konfigurasi Lanjutan

### Variabel Lingkungan

| Variabel | Keterangan | Default |
|----------|------------|---------|
| `GEMINI_API_KEY` | Gemini API Key dari Google AI Studio | — (wajib diisi via sidebar atau `.env`) |

### Model AI

Aplikasi menggunakan model **`gemini-2.5-flash`** yang dioptimalkan untuk:
- Kecepatan respons tinggi
- Pemahaman konteks data tabular
- Generasi kode Python yang akurat

---

## 🔐 Keamanan

- File `.env` **tidak pernah** di-commit ke Git (sudah dikecualikan di `.gitignore`)
- API Key tidak pernah ditampilkan dalam bentuk teks biasa di UI
- Kode yang dihasilkan AI dieksekusi dalam sandbox terisolasi
- Tidak ada akses ke file system dari dalam sandbox eksekusi

---

## 📝 Lisensi

Proyek ini dikembangkan untuk keperluan analisis data internal. Silakan sesuaikan lisensi sesuai kebutuhan Anda.
#   a i - v i s - a n a l y s i s  
 