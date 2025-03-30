
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

## 🔐 Авторизация

- Анонимные пользователи могут создавать ссылки
- Зарегистрированные пользователи получают доступ к управлению своими ссылками
- Используется JWT (access token) через `Authorization: Bearer <token>`

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

**Удаление ссылки:**

```http
DELETE /links/myalias
Authorization: Bearer <token>
```

---

## ⚙️ Переменные окружения (`.env.example`)

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
SYNC_DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLEANUP_THRESHOLD_DAYS=30
```

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

🟡 *После деплоя на Render здесь появится рабочая ссылка*

---

## 👨‍💻 Автор

Created by [nizov-as](https://github.com/nizov-as)
