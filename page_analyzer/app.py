import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.database import (
    add_check,
    add_url,
    get_checks_by_url_id,
    get_url_by_id,
    get_url_by_name,
)
from page_analyzer.database import (
    get_urls as get_all_urls,
)
from page_analyzer.parser import parse_page
from page_analyzer.url_normalizer import normalize_url, validate

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def post_url():
    url = request.form.get('url', '')
    errors = validate(url)

    if errors:
        for error in errors:
            flash(error, 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages), 422

    normalized_url = normalize_url(url)
    existing_url = get_url_by_name(normalized_url)

    if existing_url:
        flash('Страница уже существует', 'info')
        url_id = existing_url.id
    else:
        url_id = add_url(normalized_url)
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=url_id))


@app.route('/urls/<int:id>')
def show_url(id):
    url_data = get_url_by_id(id)

    if not url_data:
        return "Page not found", 404

    checks = get_checks_by_url_id(id)
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'urls/show.html',
        url=url_data,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<int:id>/checks')
def create_check(id):
    url_data = get_url_by_id(id)

    if not url_data:
        return "Page not found", 404

    try:
        response = requests.get(url_data.name)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))

    parsed_data = parse_page(response.text)

    add_check(
        id,
        response.status_code,
        parsed_data['h1'],
        parsed_data['title'],
        parsed_data['description']
    )
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))


@app.route('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template('urls/index.html', urls=urls)