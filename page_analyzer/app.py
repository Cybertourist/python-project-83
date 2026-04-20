import os
import psycopg2
from psycopg2.extras import NamedTupleCursor
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from urllib.parse import urlparse
import validators
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def validate(url):
    errors = []
    if not url:
        errors.append("URL обязателен")
    if len(url) > 255:
        errors.append("URL превышает 255 символов")
    if not validators.url(url):
        errors.append("Некорректный URL")
    return errors

@app.route('/')
def index():
    return render_template('index.html')

@app.post('/urls')
def post_url():
    url = request.form.get('url')
    errors = validate(url)
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422

    normalized_url = normalize_url(url)
    
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
        # Проверяем, существует ли уже такой URL
        curr.execute("SELECT id FROM urls WHERE name = %s", (normalized_url,))
        existing_url = curr.fetchone()
        
        if existing_url:
            flash('Страница уже существует', 'info')
            id = existing_url.id
        else:
            # Вставляем новую запись
            curr.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                (normalized_url, datetime.now())
            )
            id = curr.fetchone().id
            conn.commit()
            flash('Страница успешно добавлена', 'success')
    
    conn.close()
    return redirect(url_for('show_url', id=id))

@app.route('/urls/<int:id>')
def show_url(id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute("SELECT * FROM urls WHERE id = %s", (id,))
            url_data = curr.fetchone()
            
            if not url_data:
                return "Page not found", 404
            
            curr.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC", (id,))
            checks = curr.fetchall()
            
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls/show.html', url=url_data, checks=checks, messages=messages)

@app.post('/urls/<int:id>/checks')
def add_check(id):
    with get_db_connection() as conn:
        with conn.cursor() as curr:
            try:
                curr.execute(
                    "INSERT INTO url_checks (url_id, created_at) VALUES (%s, %s)",
                    (id, datetime.now())
                )
                conn.commit()
                flash('Страница успешно проверена', 'success')
            except psycopg2.Error:
                conn.rollback()
                flash('Произошла ошибка при проверке', 'danger')
                
    return redirect(url_for('show_url', id=id))

@app.route('/urls')
def get_urls():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute("""
                SELECT 
                    urls.id, 
                    urls.name, 
                    url_checks.created_at AS last_check, 
                    url_checks.status_code 
                FROM urls 
                LEFT JOIN url_checks ON urls.id = url_checks.url_id 
                AND url_checks.id = (
                    SELECT MAX(id) FROM url_checks WHERE url_id = urls.id
                )
                ORDER BY urls.id DESC
            """)
            urls = curr.fetchall()
            
    return render_template('urls/index.html', urls=urls)