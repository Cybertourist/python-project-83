### Hexlet tests and linter status:
[![Actions Status](https://github.com/Cybertourist/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Cybertourist/python-project-83/actions)


# Анализатор страниц (Page Analyzer)

Анализатор страниц — это веб-приложение на Flask, которое позволяет проверять сайты на доступность, а также анализировать базовые SEO-теги (h1, title, description).

### 🚀 Деплой
Приложение развернуто и доступно по ссылке: 
[https://page-analyzer-9nv7.onrender.com](https://page-analyzer-9nv7.onrender.com)

### 🛠 Стек технологий
* Python 3.10+
* Flask
* PostgreSQL
* Bootstrap 5
* BeautifulSoup4 / Requests

### 💻 Локальный запуск
1. Клонируйте репозиторий.
2. Установите зависимости: `make install`
3. Создайте файл `.env` и добавьте `DATABASE_URL` и `SECRET_KEY`.
4. Создайте базу данных и примените схему: `psql -d page_analyzer -f database.sql`
5. Запустите сервер: `make dev`
