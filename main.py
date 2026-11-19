"""
main.py - Minimal deployment and startup script for LaterNote.
Designed for platforms like Render: runs database migrations, collects
static files, and launches the production Uvicorn ASGI server.
"""

import os
import django
from django.core.management import call_command
import uvicorn

# 1. Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def deploy_and_run():
    print("🚀 [LaterNote] Starting deployment checks...")

    # 2. Run database migrations
    print("📦 [LaterNote] Applying database migrations...")
    call_command("migrate", interactive=False)

    # 3. Collect static files for WhiteNoise
    print("🎨 [LaterNote] Collecting static assets...")
    call_command("collectstatic", interactive=False)

    # 4. Read port provided by Render (default to 8000 for local runs)
    port = int(os.environ.get("PORT", 8000))

    # 5. Start Uvicorn ASGI server
    print(f"✨ [LaterNote] Uvicorn server running on http://0.0.0.0:{port}")
    uvicorn.run(
        "config.asgi:application",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    deploy_and_run()
