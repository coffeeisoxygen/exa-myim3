from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


# Device Model
class Device(SQLModel, table=True):
    """device android yang akan menjalan kan otomatisasi"""

    serial: str = Field(primary_key=True, unique=True)
    model: str
    manufacturer: str
    name: str
    note: Optional[str] = None
    is_active: bool = Field(default=False)
    is_connected: bool = Field(default=False)
    connection_test: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime = Field(default=datetime.now())


# # GSM Modem Model
# class GSMModem(SQLModel, table=True):
#     """modem gsm yang akan menerima sms dan melakukan cek nomor awal"""
#     id: Optional[int] = Field(default=None, primary_key=True)
#     port: str = Field(unique=True)
#     name: str = Field(unique=True)
#     is_active: bool = Field(default=False)
#     is_connected: bool = Field(default=False)
#     baudrate: int = Field(default=115200)
#     connection_test: Optional[str] = None
#     last_connected_at: Optional[datetime] = None
#     created_at: datetime = Field(default=datetime.now())


# # SIM Card Model
# class SimCard(SQLModel, table=True):
#     """msisdn yang akan di proses untk pembelian"""
#     msisdn: str = Field(primary_key=True)
#     iccid: Optional[str] = None
#     balance: int
#     exp_date: datetime
#     status: int = Field(default=0)  # 0=nonaktif, 1=aktif, 2=expired
#     created_at: datetime = Field(default=datetime.now())


# # Transaction Model
# class Transaction(SQLModel, table=True):
#     """table transaksi"""
#     trxid: Optional[int] = Field(default=None, primary_key=True)
#     tgl_entri: datetime
#     msisdn: str = Field(foreign_key="simcard.msisdn")
#     port: str = Field(foreign_key="gsmmodem.port")
#     trx_status: int = Field(
#         default=0
#     )  # 0=belum diproses, 1=proses, 2=berhasil, 3=gagal
#     device: str = Field(foreign_key="device.serial")
#     produk: Optional[str] = None
#     harga: Optional[int] = None
#     email: Optional[str] = None
#     sn: Optional[str] = None
#     tgl_status: datetime


# # Transaction Tracking Model
# class TransactionTracking(SQLModel, table=True):
#     """tabel tracking otomatisasi pada android"""
#     id: Optional[int] = Field(default=None, primary_key=True)
#     trxid: int = Field(foreign_key="transaction.trxid")
#     step: int
#     progress: str
#     timestamp: datetime = Field(default=datetime.now())


# # Logs Model
class Logs(SQLModel, table=True):
    """log yang menyimpan informasi penting aplikasi jika ada error atau hal hal yang penting"""

    id: Optional[int] = Field(default=None, primary_key=True)
    log_type: str
    pesan: str
    timestamp: datetime = Field(default=datetime.now())
