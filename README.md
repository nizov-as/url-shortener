
# ✂️ URL Shortener API

Простой и удобный сервис для сокращения ссылок, с авторизацией, аналитикой, сроками действия и кэшированием.  
Разработан с использованием **FastAPI**, **PostgreSQL**, **Redis**, **Docker**, **Pydantic v2** и других технологий.

---

## 🚀 Функциональность

- 🔗 Сокращение длинных ссылок (`POST /links/shorten`)
- 🧭 Редирект по короткому коду (`GET /links/{short_code}`)
- ✏️ Обновление ссылки (`PUT /links/{short_code}`)
- ❌ Удаление ссылки (`DELETE /links/{short_code}`)
- 📊 Статистика по ссылке (`GET /links/{short_code}/stats`)
- 🔍 Поиск по оригинальному URL (`GET /links/search?original_url=...`)
- 🧩 Поддержка custom alias и срока действия (`expires_at`)
- 👤 Регистрация и авторизация пользователей
- 🔐 Защита управления ссылками (только для владельцев)
- ⚡ Кэширование редиректов через Redis
- 🔁 Автоматическое удаление неиспользуемых ссылок
- ⏳ Просмотр всех истекших ссылок

---

## 🔐 Регистрация и Авторизация

- Анонимные пользователи могут создавать ссылки
- Зарегистрированные пользователи получают доступ к управлению своими ссылками
- Для регистрации использовать `POST /auth/register`
- Для авторизации нажать на Autorize в верхней части Swagger и ввести username и password в открывшемся окне

---

## 🛠️ Установка и запуск

### 1. Клонируй репозиторий

```bash
git clone https://github.com/nizov-as/url-shortener.git
cd url-shortener
```

---

### 2. Создай `.env` файл на основе шаблона

```bash
cp .env.example .env
```

Заполни актуальные данные (например, подключение к БД, ключи и т.п.)

Пример значений:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/url_shortener
SYNC_DATABASE_URL=postgresql://postgres:postgres@db:5432/url_shortener
REDIS_URL=redis://redis:6379
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLEANUP_THRESHOLD_DAYS=30
```

---

### 3. Запусти проект через Docker

```bash
docker-compose up --build
```

📌 Swagger UI будет доступен по адресу:  
http://localhost:8000/docs

---

## 🧪 Примеры запросов

**Сокращение ссылки:**

```http
POST /links/shorten
Content-Type: application/json

{
  "original_url": "https://example.com",
  "custom_alias": "myalias",
  "expires_at": "2025-04-01T12:00"
}
```

**Редирект:**

```http
GET /links/myalias → 307 Redirect → https://example.com
```

**Redis кэш:**

Редирект по myalias второй раз быстрее (идёт через Redis)

---

## 🗄️ Структура базы данных

**Таблица users**
- `id`, `email`, `hashed_password`, `created_at`

**Таблица links**
- `id`, `original_url`, `short_code`, `custom_alias`, `expires_at`, `click_count`, `last_clicked`, `user_id`, `created_at`

---

## 🧩 Дополнительные функции

- 🔁 **Удаление неиспользуемых ссылок**  
  Удаляются, если не было переходов более `N` дней (`CLEANUP_THRESHOLD_DAYS`)

- ⏳ **История истекших ссылок**  
  `GET /links/expired` возвращает все ссылки, чей срок действия истёк

---

## 🌐 Демо

🟡 [Ссылка на Демо в Render](https://url-shortener-yl7x.onrender.com/docs)

---

## Тестирование

Фреймворк: `pytest` с `pytest-asyncio`  
Изолированная среда тестирования развёрнута через `docker-compose`.

### Запуск тестов:

```bash
docker-compose -f docker-compose.test.yml up --build

---

## 👨‍💻 Автор

Created by [nizov-as](https://github.com/nizov-as)
