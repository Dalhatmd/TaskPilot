# TaskPilot Backend

A FastAPI-based backend for TaskPilot, an AI-powered task management application with user authentication and Google Gemini AI integration.

## Features

- 🔐 User authentication with JWT tokens
- 📝 CRUD operations for tasks
- 🤖 AI-powered task summarization using Google Gemini
- 🗄️ SQLite database with SQLAlchemy ORM
- 📊 Task status tracking (TODO, IN_PROGRESS, COMPLETED, CANCELLED)
- 🔍 Task filtering and search capabilities
- 📅 Due date management
- 🎯 Priority levels (low, medium, high)

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: JWT tokens
- **AI Integration**: Google Generative AI (Gemini)
- **Testing**: pytest
- **API Documentation**: Auto-generated with Swagger/OpenAPI

## Prerequisites

- Python 3.8+
- Google Gemini API key (for AI features)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd TaskPilot/backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```bash
   cp .env.example .env  # If example exists, or create manually
   ```
   
   Add the following to your `.env` file:
   ```env
   # Database
   DATABASE_URL=sqlite:///./taskpilot.db
   
   # Security
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # AI Configuration
   GOOGLE_GEMINI_API_KEY=your-google-gemini-api-key-here
   
   # CORS (for frontend integration)
   BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
   ```

## Database Setup

1. **Initialize the database**:
   ```bash
   python init_db.py
   ```
   This will create the SQLite database and all necessary tables.

## Running the Application

### Development Server

Start the FastAPI development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://127.0.0.1:8000
- **Interactive API docs (Swagger)**: http://127.0.0.1:8000/docs
- **Alternative API docs (ReDoc)**: http://127.0.0.1:8000/redoc

### Production

For production deployment:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register a new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile

### Tasks
- `GET /api/v1/tasks/` - Get user's tasks (with filtering/pagination)
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task

### AI Features
- `POST /api/v1/ai/summarize-tasks` - Generate AI summary of tasks

## Testing

### Unit Tests

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test files
pytest test_ai_service.py
pytest test_auth.py
pytest test_tasks.py
```

### Manual API Testing

Test the AI endpoints manually:

```bash
# Test AI summarization
python manual_test_ai_api.py

# Simple unit tests (no pytest required)
python simple_test_ai.py
python simple_test_ai_endpoints.py
```

### Integration Testing

Test with real AI API (requires valid Google Gemini API key):

```bash
python integration_test_ai.py
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | SQLite database URL | `sqlite:///./taskpilot.db` | No |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `GOOGLE_GEMINI_API_KEY` | Google AI API key | - | Yes (for AI features) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | `30` | No |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | No |

### Database Migration

If you need to reset the database:

```bash
rm taskpilot.db  # Delete existing database
python init_db.py  # Recreate with fresh schema
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       │   ├── auth.py     # Authentication endpoints
│   │       │   ├── tasks.py    # Task CRUD endpoints
│   │       │   └── ai.py       # AI summarization endpoints
│   │       └── api.py          # Main API router
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database setup
│   │   └── deps.py             # FastAPI dependencies
│   ├── models/                 # SQLAlchemy database models
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic layer
│   └── main.py                 # FastAPI application entry point
├── tests/                      # Test files
├── alembic/                    # Database migrations (if using Alembic)
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database initialization script
└── README.md                   # This file
```

## Development

### Adding New Features

1. **Database Models**: Add to `app/models/`
2. **API Schemas**: Add to `app/schemas/`
3. **Business Logic**: Add to `app/services/`
4. **API Endpoints**: Add to `app/api/v1/endpoints/`
5. **Tests**: Add to test files

### Code Quality

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for modules and functions
- Include unit tests for new features

## Troubleshooting

### Common Issues

1. **Database locked error**:
   ```bash
   rm taskpilot.db
   python init_db.py
   ```

2. **AI API not working**:
   - Check your `GOOGLE_GEMINI_API_KEY` in `.env`
   - Verify API key has proper permissions
   - Check network connectivity

3. **CORS errors from frontend**:
   - Update `BACKEND_CORS_ORIGINS` in `.env`
   - Ensure frontend URL is included

4. **Authentication issues**:
   - Check `SECRET_KEY` is set in `.env`
   - Verify JWT token format in requests

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT Licence: Free to copy and distribute

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the API documentation at `/docs`
- Create an issue in the repository