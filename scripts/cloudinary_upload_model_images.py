"""Upload ops/models/* to Cloudinary as public ids `models/<filename-stem>`.

Name each file after the model slug (gpt-oss-120b.png -> models/gpt-oss-120b). That public
id is what goes in `imageId` in Backend-core/src/db/seed.ts; the frontend builds the URL.
Safe to re-run: existing images are overwritten in place and their CDN cache invalidated.

    python scripts/cloudinary_upload_model_images.py
"""
import re
import sys
from pathlib import Path

import cloudinary
import cloudinary.exceptions
import cloudinary.uploader
from dotenv import load_dotenv

OPS = Path(__file__).resolve().parent.parent
MODELS_DIR = OPS / "models"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"}
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def collect(directory: Path) -> dict[str, Path]:
    """public_id -> file for every image in `directory`; exits on a bad or duplicate name."""
    found: dict[str, Path] = {}
    for f in sorted(directory.iterdir()):
        if f.suffix.lower() not in IMAGE_EXTS:
            continue
        if not SLUG.fullmatch(f.stem):
            raise SystemExit(f"{f.name}: name it after the model slug, e.g. gpt-oss-120b.png")
        public_id = f"models/{f.stem}"
        if public_id in found:
            raise SystemExit(f"{found[public_id].name} and {f.name} both map to {public_id} — keep one")
        found[public_id] = f
    return found


def main() -> None:
    files = collect(MODELS_DIR)
    if not files:
        print(f"No images in {MODELS_DIR} — drop <model-slug>.png files there and re-run.")
        return

    load_dotenv(OPS / ".env")
    cloudinary.reset_config()  # the SDK reads CLOUDINARY_URL at import time, before load_dotenv
    if not cloudinary.config().api_secret:
        sys.exit("CLOUDINARY_URL is not set — copy .env.example to .env and fill it in.")

    failed = 0
    for public_id, path in files.items():
        try:
            # invalidate: the frontend URLs carry no version, so purge the CDN copy on overwrite.
            res = cloudinary.uploader.upload(
                str(path), public_id=public_id, resource_type="image", overwrite=True, invalidate=True
            )
        except cloudinary.exceptions.Error as e:
            failed += 1
            print(f"FAIL  {path.name}: {e}")
            continue
        print(f"ok    {path.name:32} -> imageId: '{res['public_id']}'")

    print(f"\n{len(files) - failed}/{len(files)} uploaded.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
