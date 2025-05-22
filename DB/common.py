import sqlite3
import hashlib

def get_db_connection():
    conn = sqlite3.connect('./DB/silverNews.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()