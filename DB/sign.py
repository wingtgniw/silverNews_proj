import sqlite3
from .common import get_db_connection, hash_password

def create_user(name, email, password, birth_year):
    """새로운 사용자 생성"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        hashed_password = hash_password(password)
        
        c.execute('''
            INSERT INTO users (name, email, password, birth_year)
            VALUES (?, ?, ?, ?)
        ''', (name, email, hashed_password, birth_year))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # 이메일 중복
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def verify_user(email, password):
    """사용자 인증"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        hashed_password = hash_password(password)
        
        c.execute('''
            SELECT * FROM users 
            WHERE email = ? AND password = ?
        ''', (email, hashed_password))
        
        user = c.fetchone()
        return user
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """이메일로 사용자 조회"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        return user
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()

def get_all_users():
    """모든 사용자 조회"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE user_type = "V"')
        users = c.fetchall()
        return users
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []
    finally:
        conn.close()