"""
Application entry point.
"""

from venv import logger

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth import get_current_user  # Tambahkan fungsi untuk autentikasi
from app.core.config import DEBUG, HOST, PORT
from app.core.logging import initialize_logging

app = FastAPI()

# Tambahkan middleware CORS jika diperlukan
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the app. Please login or register."}


@app.get("/dashboard")
async def dashboard(user: dict = Depends(get_current_user)):
    return {"message": f"Welcome to the dashboard, {user['username']}!"}


def main():
    """Run the application server."""
    try:
        # Initialize logging
        initialize_logging(log_to_file=True)

        # Print more info
        logger.info(f"Starting server on {HOST}:{PORT}")

        # Run uvicorn server
        uvicorn.run(
            "app.app:app",
            host=HOST,
            port=PORT,
            reload=DEBUG,
            log_level="debug",  # Gunakan debug
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()
