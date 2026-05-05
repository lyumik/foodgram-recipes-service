# Foodgram — Recipes Service

Микросервис для работы с рецептами в рамках командного проекта **Foodgram Microservices + AI Meal Planner**.

**Автор**: Кузнецова Людмила  
**Роль**: Core Backend — рецепты, ингредиенты, теги, список покупок  
**Стек**: Python, Django, DRF, PostgreSQL, Docker

---

## О проекте

Foodgram — сервис рецептов с микросервисной архитектурой. Три независимых сервиса:

- **Auth Service** — авторизация, пользователи, избранное
- **Recipes Service** — рецепты, ингредиенты, список покупок ← *этот репозиторий*
- **Meal Planner Service** — AI-генерация рационов

---

## Стек технологий

- Python 3.11+
- Django 5.0+
- Django REST Framework
- PostgreSQL 16
- Docker + docker-compose
- pytest + pytest-django
- ReportLab (генерация PDF)
- django-filter
- flake8 (линтер)
- black (форматтер)

---

## Модели

| Модель | Описание |
|---|---|
| `Tag` | Тег рецепта (Завтрак, Обед и т.д.) |
| `Ingredient` | Ингредиент из справочника с единицей измерения |
| `Recipe` | Рецепт с фото, тегами и ингредиентами |
| `RecipeIngredient` | Связь рецепт и ингредиент с полем количества |
| `ShoppingCart` | Список покупок пользователя |

---

## API эндпоинты

### Теги
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/tags/` | Список всех тегов |

### Ингредиенты
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/ingredients/` | Список всех ингредиентов |

### Рецепты
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/recipes/` | Список рецептов с фильтрацией и пагинацией |
| POST | `/api/recipes/` | Создать рецепт |
| GET | `/api/recipes/{id}/` | Детальная карточка рецепта |
| PATCH | `/api/recipes/{id}/` | Обновить рецепт (только автор) |
| DELETE | `/api/recipes/{id}/` | Удалить рецепт (только автор) |

### Список покупок
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/shopping_cart/?user_id=1` | Список рецептов в корзине |
| POST | `/api/shopping_cart/{id}/` | Добавить рецепт в корзину |
| DELETE | `/api/shopping_cart/{id}/` | Удалить рецепт из корзины |
| GET | `/api/shopping_cart/download/?user_id=1` | Скачать PDF со списком покупок |

### Фильтры и сортировка

    GET /api/recipes/?tags=1
    GET /api/recipes/?tags=1&tags=2
    GET /api/recipes/?is_in_shopping_cart=1&user_id=1
    GET /api/recipes/?ordering=cooking_time
    GET /api/recipes/?ordering=-pub_date
    GET /api/recipes/?page=2

---

## Запуск

### Локально

    cd backend
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Сервис доступен на http://localhost:8000/api/

### Через Docker

    docker-compose up --build

Сервис доступен на http://localhost:8002/api/

---

## Тесты

    cd backend
    pytest -v

25 unit-тестов покрывают:

- Теги и ингредиенты
- CRUD рецептов с вложенными данными
- Permissions — 403 для чужого автора
- Пагинация и сортировка
- Корзина (добавление, список, дубли, удаление)
- Скачивание PDF
- Фильтрация по тегам и корзине
- ImageField — наличие поля и создание без фото

---

## Качество кода

### Проверка линтером

    flake8 recipes/ --max-line-length=120

### Форматирование

    black recipes/ --line-length=120

---

## Структура проекта

    foodgram/
    ├── backend/
    │   ├── config/
    │   │   ├── settings.py
    │   │   └── urls.py
    │   ├── recipes/
    │   │   ├── migrations/
    │   │   ├── fonts/
    │   │   │   └── DejaVuSans.ttf
    │   │   ├── models.py
    │   │   ├── serializers.py
    │   │   ├── views.py
    │   │   ├── urls.py
    │   │   ├── filters.py
    │   │   ├── permissions.py
    │   │   ├── admin.py
    │   │   └── tests.py
    │   ├── requirements.txt
    │   ├── manage.py
    │   ├── setup.cfg
    │   └── Dockerfile
    └── docker-compose.yml

---

## Этапы разработки

### Этап 1

- Django проект + requirements.txt
- Модели: Tag, Ingredient, Recipe
- GET /tags, /ingredients, /recipes
- 6 unit-тестов
- Dockerfile + docker-compose

### Этап 2

- Модель RecipeIngredient с полем количества
- POST/GET/PATCH/DELETE для рецептов
- Вложенные данные в GET /recipes/{id}/
- Фильтрация по тегам и корзине
- Модель ShoppingCart
- Генерация PDF с кириллицей (шрифт DejaVu)
- ImageField для фото рецептов
- Интеграция в общий docker-compose

### Этап 3

- Permissions IsAuthorOrReadOnly
- Пагинация + Ordering (?ordering=-pub_date)
- Оптимизация запросов (prefetch_related)
- MEDIA_URL + тесты изображений
- flake8 + black
- 25 финальных unit-тестов
