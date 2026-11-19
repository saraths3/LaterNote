"""
main.py - Minimal deployment and startup script for LaterNote.
Designed for platforms like Render: loads environment variables, runs
database migrations, collects static files, and launches the Uvicorn ASGI server.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# 2. Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.core.management import call_command
import uvicorn


def deploy_and_run():
    print("🚀 [LaterNote] Starting deployment checks...")

    # 3. Run database migrations
    print("📦 [LaterNote] Applying database migrations...")
    call_command("migrate", interactive=False)

    # 4. Collect static files for WhiteNoise
    print("🎨 [LaterNote] Collecting static assets for WhiteNoise...")
    call_command("collectstatic", interactive=False)

    # 5. Read port provided by Render (default to 8000 for local runs)
    port = int(os.environ.get("PORT", 8000))

    # 6. Start Uvicorn ASGI server
    print(f"✨ [LaterNote] Uvicorn server running on http://0.0.0.0:{port}")
    uvicorn.run(
        "config.asgi:application",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    deploy_and_run()
