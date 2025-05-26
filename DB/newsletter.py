from .common import get_db_connection

def insert_newsletter(user_id, result, RAG_rst):
    """
    크롤링 뉴스레터 페이지 DB 입력
    args:
        user_id: 유저 아이디
        result: 크롤링 결과
    """
    conn = get_db_connection()
    c = conn.cursor()

    crawled_keywords = result["keywords_kr"] if result["keywords_kr"] else ""
    crawled_summary = result["summary"] if result["summary"] else ""
    content = result["newsletter"] if result["newsletter"] else ""
    title = result["newsletter_title"] if result["newsletter_title"] else ""

    c.execute('''
        INSERT INTO newsletters (user_id, title, content, crawled_keywords, crawled_summary, r_score, r_result)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, title, content, crawled_keywords, crawled_summary, RAG_rst[0], RAG_rst[1]))

    conn.commit()
    conn.close()

def insert_newsletter_with_reranker(user_id, result):
    """
    크롤링 + reranker 뉴스레터 페이지 DB 입력
    args:
        user_id: 유저 아이디
        result: 크롤링 + reranker 결과
    """
    conn = get_db_connection()
    c = conn.cursor()

    keys = result.keys()

    title = result["newsletter_title"] if "newsletter_title" in keys else ""
    content_summary = result["newsletter_summary"] if "newsletter_summary" in keys else ""
    content = result["newsletter"] if "newsletter" in keys else ""
    crawled_keywords = result["keywords"] if "keywords" in keys else ""
    crawled_summary = result["summary"] if "summary" in keys else ""

    c.execute('''
        INSERT INTO newsletters (user_id, title, content_summary, content, crawled_keywords, crawled_summary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, content_summary, content, crawled_keywords, crawled_summary))

    conn.commit()
    conn.close()

def get_newsletter(user_id):
    """
    뉴스레터 페이지 DB 조회
    args:
        user_id: 유저 아이디
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        SELECT * FROM newsletters WHERE user_id = ?
    ''', (user_id,))

    return c.fetchall()

def get_all_newsletters(user_id):
    """
    모든 뉴스레터 조회
    args:
        user_id: 유저 아이디
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        SELECT * FROM newsletters WHERE user_id = ?
    ''', (user_id,))

    return c.fetchall()

def get_newsletter_by_id(id):
    """
    뉴스레터 페이지 DB 조회
    args:
        id: 뉴스레터 아이디
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        SELECT * FROM newsletters WHERE id = ?
    ''', (id,))

    return c.fetchone()

def update_newsletter(id, title, content_summary, content):
    """
    뉴스레터 페이지 DB 수정
    args:
        id: 뉴스레터 아이디
        title: 뉴스레터 제목
        content_summary: 뉴스레터 요약
        content: 뉴스레터 내용
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        UPDATE newsletters SET title = ?, content_summary = ?, content = ? WHERE id = ?
    ''', (title, content_summary, content, id))

    conn.commit()
    conn.close()

def delete_newsletter(id):
    """
    뉴스레터 페이지 DB 삭제
    args:
        id: 뉴스레터 아이디
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        DELETE FROM newsletters WHERE id = ?
    ''', (id,))

    conn.commit()
    conn.close()



def get_newsletter_keywords_by_id(id):
    """
    뉴스레터의 키워드(crawled_keywords)만 조회
    args:
        id: 뉴스레터 아이디

    return:
        crawled_keywords (str) 또는 None
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        SELECT crawled_keywords FROM newsletters WHERE id = ?
    ''', (id,))
    
    result = c.fetchone()
    conn.close()

    return result[0] if result else None
