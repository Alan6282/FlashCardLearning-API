# DRF FlashCardLearning API v1.0.0

The API features JWT-based authentication and enables users to manage flashcard learning by creating and organizing decks and cards, reviewing content, and tracking learning progress with detailed statistics. It provides secure user access, progress insights, and a scalable backend suitable for modern learning applications.

Complete FlashCard learning backend using Django, Django REST Framework, and Redis caching.

- JWT auth with refresh/token blacklist
- Deck and Flashcard CRUD
- Review history + SM-2 spaced repetition progress
- User/deck level stats
- Caching and invalidation
- Swagger docs with drf_yasg

---

## **Table of Contents**
-  ⚙️ [**Installation**](#installation)
-  🗂️ [**Project Structure**](#project-structure)
-  ⭐ [**Features**](#features)
-  🔁 [**Spaced Repetition Algorithm**](#spaced-repetition-algorithm) 
-  🌐 [**API Endpoints**](#api-endpoints)
-  ⚡ [**Cache & Invalidation**](#cache--invalidation)
- 🧪 [**Testing**](#testing)
- 🚀 [**Future Enhancements**](#future-enhancements)

---

##  **Installation**

**1. Clone repository**
   ```bash
   git clone https://github.com/Alan6282/FlashCardLearning-API.git
   cd FlashCardLearning-API
   ```

**2. Setup virtualenv**

   Windows
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   macOS/Linux
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

**3. Install dependencies**
   ```bash
   pip install -r requirements/base.txt
   ```

**4. Install and run Redis (for caching)**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```
   Verify Redis is running: 

   ```bash     
    docker ps 
   ```

**5. Configure Environment Variables**
  
   Copy environment template

   Windows 
   ```bash
    copy .sample.env .env
   ```

   macOS/Linux
   ```bash 
     cp sample.env .env
   ``` 


**6. Set variables in `.env` (or environment)**
   ```dotenv
   # Generate SECRET_KEY with: python scripts/generate_secret_key.py
   SECRET_KEY=your-generated-secret-key-here

   DEBUG=True  # Set to False in production

   # Database settings (PostgreSQL)
   DB_NAME=your_database_name
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=localhost  # or your DB host IP
   DB_PORT=5432  # PostgreSQL default port
   ```

**7. Generate new key (optional)**
   ```bash
   python scripts/generate_secret_key.py
   ```

**8. Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

**9. Create Superuser**
   ```bash
   python manage.py createsuperuser
   ``` 
    
   
   
   

**10. Start Development Server**
   ```bash
    python manage.py runserver
   ```

   Your API Will be Available at

   ```http
    http://127.0.0.1.8000/
   ``` 

   #### API Documentation

   Swagger UI :```http://127.0.0.1:8000/swagger/```

   ReDoc:```http://127.0.0.1:8000/redoc/```


[🔼 Back to Top](#drf-flashcardlearning-api-v100)

---

##  **Project Structure**

 ```
 📂FlashCard_Learning_API
  ┣  📂apps                         # Custom django apps(users ,flashcards)
  ┃  ┣ 📂flashcards                 # Flashcards ( cards & Reviews )
  ┃  ┃ ┣ 📂serializers
  ┃  ┃ ┃ ┣ 📜__init__.py
  ┃  ┃ ┃ ┣ 📜base.py
  ┃  ┃ ┃ ┣ 📜cards.py
  ┃  ┃ ┃ ┣ 📜decks.py
  ┃  ┃ ┃ ┣ 📜review.py
  ┃  ┃ ┃ ┣ 📜stats.py
  ┃  ┃ ┃ ┗ 📜suggestion.py
  ┃  ┃ ┃
  ┃  ┃ ┣ 📂views
  ┃  ┃ ┃ ┣ 📜__init__.py
  ┃  ┃ ┃ ┣ 📜base.py             # Import common dependencies for views 
  ┃  ┃ ┃ ┣ 📜cards.py
  ┃  ┃ ┃ ┣ 📜decks.py
  ┃  ┃ ┃ ┣ 📜review.py
  ┃  ┃ ┃ ┣ 📜stats.py
  ┃  ┃ ┃ ┗ 📜suggestion.py
  ┃  ┃ ┃
  ┃  ┃ ┣ 📜__init__.py
  ┃  ┃ ┣ 📜admin.py
  ┃  ┃ ┣ 📜apps.py
  ┃  ┃ ┣ 📜models.py
  ┃  ┃ ┣ 📜paginators.py
  ┃  ┃ ┣ 📜signals.py
  ┃  ┃ ┣ 📜tests.py
  ┃  ┃ ┗ 📜urls.py
  ┃  ┃
  ┃  ┗ 📂users                 # Users app (user auth & authorization)
  ┃    ┣ 📂serializers
  ┃    ┃ ┣ 📜__init__.py
  ┃    ┃ ┣ 📜login.py
  ┃    ┃ ┣ 📜logout.py
  ┃    ┃ ┣ 📜register.py
  ┃    ┃ ┣ 📜token_refresh.py
  ┃    ┃ ┗ 📜userinfo.py
  ┃    ┣ 📂views
  ┃    ┃ ┣ 📜__init__.py
  ┃    ┃ ┣ 📜base.py       # Import Common dependencies for views 
  ┃    ┃ ┣ 📜login.py
  ┃    ┃ ┣ 📜logout.py
  ┃    ┃ ┣ 📜register.py
  ┃    ┃ ┗ 📜token_refresh.py
  ┃    ┣ 📜__init__.py
  ┃    ┣ 📜admin.py
  ┃    ┣ 📜apps.py
  ┃    ┣ 📜models.py
  ┃    ┣ 📜tests.py
  ┃    ┣ 📜throttles.py  # Rate-Limiting Configs for Users App 
  ┃    ┗ 📜urls.py
  ┣  📂config
  ┃  ┣ 📂settings
  ┃  ┃ ┣ 📜__init__.py
  ┃  ┃ ┣ 📜base.py       # shared common settings
  ┃  ┃ ┣ 📜development.py # Dev-env specific settings 
  ┃  ┃ ┣ 📜production.py  # Prod-env specific settings
  ┃  ┃ ┗ 📜test.py        # Test-env specific settings
  ┃  ┣ 📜__init__.py
  ┃  ┣ 📜asgi.py
  ┃  ┣ 📜swagger_schema.py
  ┃  ┣ 📜urls.py
  ┃  ┗ 📜wsgi.py
  ┣  📂requirements
  ┃  ┣ 📜base.txt
  ┃  ┣ 📜dev.txt
  ┃  ┣ 📜prod.txt
  ┃  ┗ 📜test.txt
  ┣  📂scripts
  ┃  ┗ 📜generate_secret_key.py  # Django secret key generator 
  ┣  📂tests
  ┃  ┣ 📂flashcards              # Flashcards app tests
  ┃  ┃ ┣ 📂test_models           # Model tests
  ┃  ┃ ┣ 📂test_serializers      # Serializers tests 
  ┃  ┃ ┣ 📂test_views            # Views tests 
  ┃  ┃ ┗ 📜__init__.py
  ┃  ┣ 📂users                   # Users app test 
  ┃  ┃ ┣ 📂test_models           # Model tests
  ┃  ┃ ┣ 📂test_serializers      # Serializers tests 
  ┃  ┃ ┣ 📂test_views            # Views tests 
  ┃  ┃ ┗ 📜__init__.py
  ┃  ┃
  ┃  ┣ 📜__init__.py 
  ┃  ┗ conftest.py               # Pytest configuration and fixtures
  ┣  📂utils
  ┃  ┣ 📜__init__.py
  ┃  ┗ 📜throttles.py           # Global rate-limiting utils 
  ┣  📜.env                     # Environment variables for dev-env & test-env (not in git)
  ┣  📜.gitignore
  ┣  📜sample.env               # Example environment variables 
  ┣  📜pytest.ini               # Pytest configuration 
  ┣  📜manage.py
  ┗  📜README.md         
```

[🔼 Back to Top](#drf-flashcardlearning-api-v100)

---

## **Features**

- User registration/login/logout with JWT
- Card/Deck CRUD with per-user ownership enforcement
- Review history with `known`, `quality`, and `reviewed_at`
- SM-2 spaced repetition algorithm (learned from [thyagoluciano/sm2](https://github.com/thyagoluciano/sm2) and [Wikipedia](https://en.wikipedia.org/wiki/SuperMemo)) in `CardProgress.update_sm2()` for optimal review scheduling based on user performance
- Stats endpoints for user-level and deck-level insights
- Suggestions for due cards (global/deck)
- Request throttling + filtering + pagination
- Redis caching with invalidation on write operations
- Comprehensive logging for debugging and monitoring


### Authentication

The API uses a two-token JWT model via `djangorestframework-simplejwt.`

| Token   | Lifetime | Purpose                            |
|---------|---------:|------------------------------------|
| Access  |   30 min | Authorize protected API requests   |
| Refresh |   7 days | Rotate tokens / terminate session  |

##### Lifecycle

  - Register — issues token pair immediately on account creation.
  - Login — validates credentials and issues a fresh token pair.
  - Refresh — submits refresh token, receives new pair; old token is blacklisted.
  - Logout — blacklists the refresh token, terminating the session.

#### Request format

   ```http 
    Authorization: Bearer <access_token>
   ```
#### JWT configuration

   ```python 
   ACCESS_TOKEN_LIFETIME      = 30 minutes
   REFRESH_TOKEN_LIFETIME     = 7 days
   ROTATE_REFRESH_TOKENS      = True
   BLACKLIST_AFTER_ROTATION   = True
   ```
#### Security controls
  - Stateless — no server-side session state; every request carries a signed token.
  - Token rotation — refresh tokens are single-use; reuse is detected and rejected.
  - Brute-force protection — auth endpoints are rate-limited.

### Pagination 

All list endpoints are paginated. The response always follows this structure:

```json 
  {
    "count": 100,
    "next": "https://api/endpoint/?page=2",
    "previous": null,
    "results": []
  }
```

### Client params:

```http 
GET /api/endpoint/                  # Page 1, default size
GET /api/endpoint/?page=2           # Page 2
GET /api/endpoint/?page_size=20     # Custom page size
```


## **Spaced Repetition Algorithm**

This app uses the SM-2 algorithm for spaced repetition, which dynamically adjusts the intervals between card reviews based on the user's self-assessed quality of recall (0-5 scale). It optimizes long-term retention by spacing reviews further apart as mastery increases, while resetting for poor performance. This is more effective than fixed-interval methods for efficient learning.

The SM-2 algorithm schedules each card's next review based on the user's self-rated recall quality (0–5). Poor recall resets the interval; good recall extends it exponentially, guided by an ease factor.


### Quality Scale

| Quality | Meaning |
|----------|----------|
| 0 | Complete blackout |
| 1 | Incorrect, but familiar on seeing the answer |
| 2 | Incorrect, but easy to recall after seeing the answer |
| 3 | Correct with significant difficulty |
| 4 | Correct after hesitation |
| 5 | Perfect recall |


```known = quality >= 3 ```

### Interval Progression (Example: EF = 2.5)

| Review Attempt | Quality | Interval (days) |
|----------------|---------|-----------------|
| 1st Review | 4 | 1 |
| 2nd Review | 4 | 6 |
| 3rd Review | 4 | 15 |
| 4th Review | 4 | 37 |
| Any Review | `< 3` | Reset → 1 |

---

### Ease Factor Update Formula

EF = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))

- **EF** = Ease Factor
- **q** = Quality score (`0–5`)
- **Minimum EF** = `1.3`

---
### Ease Factor Behavior

- High quality scores increase the ease factor.
- Low quality scores decrease the ease factor.
- Difficult cards remain on shorter review intervals.
- Easy cards gradually move to longer review intervals automatically.


Sources: [thyagoluciano/sm2 GitHub](https://github.com/thyagoluciano/sm2), [SuperMemo Wikipedia](https://en.wikipedia.org/wiki/SuperMemo).

[🔼 Back to Top](#drf-flashcardlearning-api-v100)

---

## **API Endpoints**

### Auth
- `POST /api/users/register/`
- `POST /api/users/login/`
- `POST /api/users/logout/`
- `POST /api/users/token/refresh/`

### Decks
- `GET /api/decks/`
- `POST /api/decks/`
- `GET /api/decks/<deck_id>/`
- `PUT/PATCH /api/decks/<deck_id>/`
- `DELETE /api/decks/<deck_id>/`

### Cards
- `GET /api/deck/<deck_id>/cards/`
- `POST /api/deck/<deck_id>/cards/`
- `GET /api/cards/<card_id>/`
- `PUT/PATCH /api/cards/<card_id>/`
- `DELETE /api/cards/<card_id>/`

### Reviews
- `GET /api/reviews/`
- `GET /api/reviews/<review_id>/`
- `GET /api/cards/<card_id>/reviews/`
- `POST /api/cards/<card_id>/reviews/`

### Suggestions
- `GET /api/suggestions/review/`
- `GET /api/suggestions/deck/<deck_id>/review/`

### Stats
- `GET /api/stats/user/`
- `GET /api/stats/deck/<deck_id>/`

[🔼 Back to Top](#drf-flashcardlearning-api-v100)

---

## **Cache & Invalidation**

- Uses Django Redis cache in `config/settings/base.py`.
- Cache keys are built by user and query params, e.g. `user_<id>_deck_list_<sorted_params>`.
- Invalidation functions:
  - `invalidate_user_cache(user.id, key_type='deck_list|card_list|suggestion_list')`
  - `invalidate_deck_user_cache(user.id, 'decksuggestion_list', deck_id=...)`
- Mutations (`POST/PUT/PATCH/DELETE`) call invalidation to keep read caches consistent.

---

## **Testing**

This project uses **pytest** as the testing framework, which is a powerful and flexible tool for writing and running tests in Python. Pytest automatically discovers test files and functions (e.g., `test_*.py` or `*_test.py`), supports fixtures for setup/teardown, assertions, and plugins for coverage and more.

### How Pytest Works
- **Discovery**: Scans for test files in the project (e.g., `apps/flashcards/tests.py`).
- **Execution**: Runs test functions/methods, checking assertions.
- **Reporting**: Outputs results, failures, and coverage if configured.
- **Integration**: Works with Django via `pytest-django` for model/view testing.

### Requirements File: test.txt
The `requirements/test.txt` file lists dependencies specifically for testing (e.g., pytest, pytest-django, coverage). It ensures a clean environment for tests without production dependencies.

### Why test.txt?
- **Isolation**: Keeps test dependencies separate from base/dev/prod.
- **Reproducibility**: Ensures consistent test environment.
- **Efficiency**: Install only what's needed for testing.

Run all tests:
```bash
pytest
```



Run specific apps:
```bash
pytest tests/flashcards
pytest tests/users
```

Run tests with coverage (if configured):
```bash
coverage run -m pytest
coverage report --skip-covered
```

[🔼 Back to Top](#drf-flashcardlearning-api-v100)

---

## **Future Enhancements**

- Add per-user and per-deck role/permission layers
- Add public decks and sharing features
- WebSocket notifications for due cards
- Docker compose for local and production

---

## Notes

- **SECRET_KEY**: Always generate a unique key using `python scripts/generate_secret_key.py` for security. Never use default or shared keys.
- Ensure `DEBUG=False` in production to prevent sensitive data exposure.
- Keep `SECRET_KEY` and DB credentials secret; use environment variables or secure vaults.
- Use proper DB credentials and connection security (e.g., SSL for production).

[🔼 Back to Top](#drf-flashcardlearning-api-v100)