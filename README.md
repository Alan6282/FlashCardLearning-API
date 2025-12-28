### DRF FlashCardLearning API **v1.0.0** 

The API features JWT-based authentication and enables users to manage flashcard learning by creating and organizing decks and cards, reviewing content, and tracking learning progress with detailed statistics. It provides secure user access, progress insights, and a scalable backend suitable for modern learning applications.


----


# 🔗 Jump To
-  ⚙️ [**Installation Guide**]()
-  🗂️ [**Project Structure**]()
-  ✨ [**Key Features**]()
   - 🔑 [**JWT-Based Authentication System**]()
   - ⏳[**Rate Limiting & Request Throttling**]()
   - 📄 [**Pagination & Response Management**]()
-  🚀 [**Future Enhancements**]()

# Installation Guide

1. **Clone the Repository** 
   ```bash
   git clone 
   cd  FlashCardLearning-API
   ```
2. Create & Activate Virtual Environment 
   ```bash 
   # windows

   python -m venv env
   .\env\scripts\activate
   ```
   ```bash
   # macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```
3. Install Dependencies
  
   ```bash 
   pip install -r requirements.txt
   ```
4. Configure Environment Variables

   ```bash
   SECRET_KEY=your-secret-key # Generate from running  "python generate_secret_key.py" in scripts 
   DEBUG=True
   DB_NAME=your-dbname
   DB_USER=your-dbusername
   DB_PASSWORD=your-dbpassword
   DB_HOST=your-dbhost
   DB_PORT=your-dbportnumber
   ```
5. Run Database Migrations

   ```bash
   python manage.py makemigrations 
   python manage.py migrate 
   ```

6. Start the Development Server 

   ```bash 
   python manage.py runserver 
   ```
   Your API Will be Available at 

   ```
   http://127.0.0.1.8000/
   ```
# 🗂️ Project Structure 
The project follows a modular Django architecture, separating concerns into dedicated applications and configuration layers. Core functionality is divided into feature-based apps, while environment-specific settings and shared utilities are centralized for maintainability, scalability, and clarity.

```

 📂FlashCard_Learning_API
  ┣ 📂apps
  ┃ ┣ 📂flashcards
  ┃ ┃ ┣ 📂serializers
  ┃ ┃ ┃ ┣ 📜__init__.py
  ┃ ┃ ┃ ┣ 📜base.py
  ┃ ┃ ┃ ┣ 📜cards.py
  ┃ ┃ ┃ ┣ 📜decks.py
  ┃ ┃ ┃ ┣ 📜review.py
  ┃ ┃ ┃ ┣ 📜stats.py
  ┃ ┃ ┃ ┗ 📜suggestion.py
  ┃ ┃ ┣ 📂views
  ┃ ┃ ┃ ┣ 📜__init__.py
  ┃ ┃ ┃ ┣ 📜base.py
  ┃ ┃ ┃ ┣ 📜cards.py
  ┃ ┃ ┃ ┣ 📜decks.py
  ┃ ┃ ┃ ┣ 📜review.py
  ┃ ┃ ┃ ┣ 📜stats.py
  ┃ ┃ ┃ ┗ 📜suggestion.py
  ┃ ┃ ┣ 📜__init__.py
  ┃ ┃ ┣ 📜admin.py
  ┃ ┃ ┣ 📜apps.py
  ┃ ┃ ┣ 📜models.py
  ┃ ┃ ┣ 📜paginators.py
  ┃ ┃ ┣ 📜signals.py
  ┃ ┃ ┣ 📜tests.py
  ┃ ┃ ┗ 📜urls.py
  ┃ ┗ 📂users
  ┃   ┣ 📂serializers
  ┃   ┃ ┣ 📜__init__.py
  ┃   ┃ ┣ 📜login.py
  ┃   ┃ ┣ 📜logout.py
  ┃   ┃ ┣ 📜register.py
  ┃   ┃ ┣ 📜token_refresh.py
  ┃   ┃ ┗ 📜userinfo.py
  ┃   ┣ 📂views
  ┃   ┃ ┣ 📜__init__.py
  ┃   ┃ ┣ 📜base.py
  ┃   ┃ ┣ 📜login.py
  ┃   ┃ ┣ 📜logout.py
  ┃   ┃ ┣ 📜register.py
  ┃   ┃ ┗ 📜token_refresh.py
  ┃   ┣ 📜__init__.py
  ┃   ┣ 📜admin.py
  ┃   ┣ 📜apps.py
  ┃   ┣ 📜models.py
  ┃   ┣ 📜tests.py
  ┃   ┣ 📜throttles.py
  ┃   ┗ 📜urls.py
  ┣ 📂config
  ┃ ┣ 📂settings
  ┃ ┃ ┣ 📜__init__.py
  ┃ ┃ ┣ 📜base.py
  ┃ ┃ ┣ 📜development.py
  ┃ ┃ ┗ 📜production.py
  ┃ ┣ 📜__init__.py
  ┃ ┣ 📜asgi.py
  ┃ ┣ 📜swagger_schema.py
  ┃ ┣ 📜urls.py
  ┃ ┗ 📜wsgi.py
  ┣ 📂requirements
  ┃ ┣ 📜base.txt
  ┃ ┣ 📜dev.txt
  ┃ ┣ 📜prod.txt
  ┃ ┗ 📜test.txt
  ┣ 📂scripts
  ┃ ┗ 📜generate_secret_key.py
  ┣ 📂utils
  ┃ ┣ 📜__init__.py
  ┃ ┗ 📜throttles.py
  ┣ 📜.env
  ┣ 📜.gitignore
  ┣ 📜manage.py
  ┗ 📜README.md
```





# ✨ Key Features 

## 🔑 JWT-Based Authentication System

This feature allows users to securely create an account and log in to the application using JSON Web Tokens (JWT). Once authenticated, users receive access and refresh tokens that protect their session and ensure only authorized users can access protected features. The system also supports safe logout and token renewal, providing a secure and reliable authentication flow.


### Token Model 
The API uses a two-token model to balance security and usability:
    
   - **Access Token**

      A short-lived JWT used to authorize protected API requests. It must be included in every authenticated request and is validated on the server without maintaining session state.
   
   - **Refresh Token** 

      A long-lived JWT used exclusively to obtain new access tokens and to explicitly terminate user sessions during logout.

### Authentication Lifecycle

1. **User Registration**

      New users are created through a dedicated registration endpoint. Upon successful account creation, the API immediately issues authentication tokens, allowing the user to access protected resources without a separate login step.
      

      ```
      
      ```
2.  **User Login**
     
      User credentials are validated using Django’s authentication backend. On successful authentication, a fresh token pair is issued.

      ```

      ```
3. **Token Renewal**
    
    When an access token expires, the client can request a new one by submitting a valid refresh token. The system rotates refresh tokens on each use, invalidating the previous token to prevent replay attacks.

    ```

    ```

4.  **Logout**

    Logout is implemented as an explicit session invalidation process. The submitted refresh token is immediately blacklisted, preventing further token refresh operations and effectively terminating the session.

    ```

    ```

### Security Controls 

-  **Stateless Authorization** :
    All protected endpoints require a valid access token in the Authorization header using the Bearer scheme.
-  **Token Rotation & Blacklisting** : Refresh tokens are rotated automatically, and previous tokens are blacklisted to prevent reuse.

- **Request Throttling** : Authentication endpoints are rate-limited to mitigate brute-force and abuse attempts.

- **Cryptographic Integrity** : Tokens are signed using a symmetric algorithm and verified on every request.


### Configuration Overview

Authentication behavior is controlled through centralized JWT configuration, defining token lifetimes, rotation behavior, header schemes, and blacklist enforcement.

```python 
ACCESS_TOKEN_LIFETIME = 30 minutes
REFRESH_TOKEN_LIFETIME = 7 days
ROTATE_REFRESH_TOKENS = True
BLACKLIST_AFTER_ROTATION = True
AUTH_HEADER = Bearer
```

### Client Request Format

All protected API requests must include the access token:

```
Authorization: Bearer <access_token>
```
### Error Handling 

- **401 Unauthorized** : Returned when tokens are missing, expired, or invalid.

- **400 Bad Request** : Triggered by malformed token payloads or missing required fields.

- **429 Too Many Requests** : Returned when rate limits are exceeded.



# ⏳ Rate Limiting & Request Throttling

To ensure system stability and prevent abusive usage patterns, the API applies layered rate limiting rules based on user type and request context.




# 📄 Pagination & Response Management

To efficiently handle large datasets and maintain consistent API performance, the application uses a configurable pagination system with endpoint-specific limits.

### **Pagination Strategy**

Different endpoints apply pagination rules based on the type and volume of data they return. This ensures balanced responses and avoids over-fetching unnecessary records.



- **Standard Paginated Response Structure**
   ```json
   {
      "count": 100, //total number of available records
      "next": "url?page=2", //link to the next page (if available)
      "previous": null, //link to the previous page
      "results": [] //data for the current page
  }
   ```

- **Client Usage Patterns**

   Clients can navigate paginated endpoints using standard query parameters:

    - Default pagination : `GET /api/endpoint/`
    - Request a specific page : `GET /api/endpoint/?page=2`
    - Override page size  : `GET /api/endpoint/?page_size=20`


# ⚡ Caching

To improve response times and minimize unnecessary database queries, the API integrates a **Redis**-based caching layer with carefully designed cache keys and invalidation rules.

### Cache Architecture

 - This API uses **Redis** as the primary cache backend through Django’s caching framework.
 - Cached data is stored in-memory within Redis for fast read access.
 - Most read-heavy endpoints use a time-based cache expiration strategy combined with explicit invalidation on data changes.




# ❌ Error Handling & Fault Management

The API applies a structured and predictable error-handling strategy to ensure reliability, debuggability, and clear communication with clients.

#### **Unified Error Response Contract**

All error responses are returned in a simple, consistent JSON format, allowing clients to handle failures uniformly across endpoints:

```json
{
  "detail": "Human-readable error description"
}
```

This format is used for validation errors, authentication failures, permission issues, and unexpected server errors.

#### **HTTP Status Code Semantics**

The API strictly adheres to RESTful status code conventions:

- `200 OK` : Request completed successfully
- `201 Created` : Resource created successfully
- `204 No Content` : Successful logout or deletion
- `400 Bad Request` : Invalid input or malformed request 
- `401 Unauthorized` : Authentication failure or invalid token 
- `403 Forbidden` : Permission or role-based access validation 
- `404 Not Found` : Requested resource does not exist
- `429 Too Many Requests` : Rate limit exceeded 
- `500 Internal Server Error` : Unhandled server-side failure 


# **🚀 Future Enhancements**

Planned improvements and features to further enhance functionality, performance, and scalability:

- **Spaced Repetition Algorithm**

  Implement intelligent scheduling to optimize review intervals based on user performance.

- **Advanced Analytics & Insights**

  Provide deeper learning metrics, progress trends, and performance visualizations.

- **Asynchronous Background Tasks**

  Use Celery and Redis for handling long-running operations such as statistics generation.

- **WebSocket / Real-Time Updates**

  Deliver live updates for progress tracking and leaderboards using Django Channels.




  
