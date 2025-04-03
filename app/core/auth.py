from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validasi token (contoh sederhana, gunakan JWT untuk produksi)
    if token != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"username": "test_user"}  # Ganti dengan data pengguna sebenarnya
