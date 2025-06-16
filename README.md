# KPU Backend

Backend untuk aplikasi surat kpu - Sistem pengelolaan surat masuk dan keluar.

## Setup

1. Buat virtual environment:
```bash
python -m venv .venv
source venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:
```bash
python app.py
```

## Struktur Direktori

```
backend_kpu/
├── app.py                 # Entry point aplikasi
├── requirements.txt       # Daftar dependensi
├── src/
│   ├── api/             # API endpoints
│   ├── database/        # Konfigurasi dan model database
│   │   ├── models/      # Model database
│   │   └── migrations/  # Migrasi database
│   ├── storage/         # Penyimpanan file
│   └── utils/           # Utility functions
```

## API Endpoints

### Auth
- `POST /api/auth/login`: Login user
- `POST /api/auth/register`: Register user baru
