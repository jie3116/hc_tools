# Human Capital Portal

Portal Human Capital berbasis Django untuk:
- pengelolaan data karyawan
- penyimpanan dokumen kebijakan HC
- permohonan surat keterangan kerja
- workflow review admin dan approval
- API JSON untuk client lain, termasuk Flutter

Project ini juga memiliki client Flutter sederhana di `flutter_hc_app/`.

## Fitur Utama

- Dashboard ringkas untuk statistik permohonan surat
- CRUD data karyawan
- Upload template surat `.docx`
- Upload dokumen kebijakan HC
- Chatbot kebijakan berbasis pencarian dokumen sederhana
- Permohonan surat oleh employee
- Review oleh admin HC
- Approval oleh approver
- Generate file surat `.docx` setelah approval
- API berbasis Django REST Framework
- Role dasar:
  - `employee`
  - `admin_hc`
  - `approver`

## Stack

- Python 3.13
- Django 6
- Django REST Framework
- PostgreSQL atau SQLite
- `python-docx`
- Flutter (subproject client)

## Struktur Direktori

```text
config/                 Konfigurasi Django
human_capital/          App utama HC
templates/              Template HTML
static/                 Static assets
media/                  Upload template dan file generated
flutter_hc_app/         Client Flutter sederhana
manage.py               Entry point Django
```

## Setup Lokal

1. Buat virtual environment dan install dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Buat file `.env` dari `.env.example`.

Contoh minimal untuk lokal:

```env
DJANGO_SECRET_KEY=ganti-dengan-secret-yang-aman
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Jika ingin memakai PostgreSQL, isi juga:

```env
DB_NAME=hc_tools
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Jika `DB_NAME` tidak diisi, aplikasi akan fallback ke SQLite lokal `db.sqlite3`.

3. Jalankan migrasi:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

4. Buat role default:

```powershell
.\.venv\Scripts\python.exe manage.py bootstrap_roles
```

5. Seed data demo:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py seed_demo_users
```

6. Jalankan server:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## Login Demo

Setelah menjalankan `seed_demo_users`, akun berikut akan tersedia:

- `hc-admin / hc-admin-123`
- `hc-approver / hc-approver-123`
- `hc-employee / hc-employee-123`

Login web:

- `http://127.0.0.1:8000/accounts/login/`

Admin Django:

- `http://127.0.0.1:8000/admin/`

Catatan:
- `hc-admin` dan `hc-approver` dibuat sebagai `is_staff`
- `hc-employee` di-link ke employee demo `EMP-001`

## Workflow Surat

1. Employee membuat permohonan surat
2. Status awal: `submitted`
3. Admin HC review:
   - approve -> `pending_approval`
   - reject -> `rejected`
4. Approver review:
   - approve -> `approved` dan file `.docx` digenerate
   - reject -> `rejected`

Workflow sudah dibatasi supaya status tidak bisa dilompati sembarang.

## Role dan Akses

- `employee`
  - bisa login
  - bisa melihat permohonan miliknya sendiri
  - bisa membuat permohonan untuk profil employee yang terhubung ke akunnya
  - bisa mengakses chatbot kebijakan

- `admin_hc`
  - bisa mengelola data karyawan
  - bisa mengelola template dan dokumen kebijakan
  - bisa review permohonan surat pada tahap admin

- `approver`
  - bisa melihat permohonan
  - bisa memberi approval akhir
  - bisa mengakses chatbot kebijakan

## API

Endpoint utama:

- `GET/POST /api/employees/`
- `GET/POST /api/policies/`
- `GET/POST /api/templates/`
- `GET/POST /api/requests/`
- `POST /api/chatbot/`

Semua endpoint API membutuhkan autentikasi.

Catatan:
- API saat ini memakai `SessionAuthentication` dan `BasicAuthentication`
- employee hanya bisa melihat request miliknya sendiri

## Flutter Client

Subproject Flutter ada di:

```text
flutter_hc_app/
```

Client ini masih sederhana dan saat ini:
- mengambil data employee dan request dari API
- memakai base URL default `http://10.0.2.2:8000/api`
- sudah memiliki error handling dasar untuk response gagal

Sebelum dipakai serius, client ini masih perlu:
- layar login
- penyimpanan credential/token
- konfigurasi environment per target
- state management yang lebih rapi

## Management Commands

- `bootstrap_roles`  
  Membuat group default: `employee`, `admin_hc`, `approver`

- `seed_demo`  
  Membuat employee, policy, dan template demo

- `seed_demo_users`  
  Membuat user demo, assign role, dan link user employee ke profil employee

## Testing

Jalankan:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Cakupan test saat ini mencakup:
- akses login
- pembatasan akses berdasarkan role
- scoping data request untuk employee
- submit request via web dan API
- validasi workflow
- generate dokumen
- onboarding user demo

## Catatan Operasional

- Untuk production, set `DJANGO_SECRET_KEY` dari environment dan jangan pakai credential demo.
- `DEBUG` default project ini dirancang `False` jika env tidak mengaktifkannya.
- File generated surat disimpan di `media/generated/`.
- Template surat sebaiknya memakai placeholder seperti:
  - `{{request_no}}`
  - `{{full_name}}`
  - `{{employee_code}}`
  - `{{department}}`
  - `{{position}}`
  - `{{purpose}}`
  - `{{recipient_name}}`
  - `{{today}}`

## Pengembangan Lanjutan

Area berikut masih layak dilanjutkan:

- halaman internal untuk manajemen user dan role tanpa masuk Django admin
- audit log untuk review/approval
- notifikasi email atau in-app
- pagination dan filtering API
- upload policy berbasis file, bukan hanya text area
- autentikasi API yang lebih layak untuk mobile client
- test coverage yang lebih luas untuk template, form, dan API error cases
