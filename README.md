# krri-ops

One-off ops scripts for Cloudinary, Supabase, Mixpanel and analytics. One script per task in `scripts/`, prefixed by service (`cloudinary_…`, `supabase_…`), each runnable on its own.

## Setup

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # then fill in the credentials
```

## Scripts

| Script | What it does |
| --- | --- |
| `scripts/cloudinary_upload_model_images.py` | Uploads `models/<slug>.<ext>` to Cloudinary as public id `models/<slug>`. Re-runnable. |

```
.venv/bin/python scripts/cloudinary_upload_model_images.py
```
