from __future__ import annotations

import os

import uvicorn


HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))


def run() -> None:
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False, app_dir="backend")


if __name__ == "__main__":
    run()
