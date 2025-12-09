# Environment Variables Reference

Complete reference for all environment variables used in the OpenAI Code Interpreter Explorer.

## Backend Environment Variables

All backend environment variables should be placed in `backend/.env` file.

### Required Variables

#### OPENAI_API_KEY
- **Description**: Your OpenAI API key for accessing the API
- **Required**: ✅ Yes
- **Default**: None
- **Example**: `sk-proj-abc123...xyz789`
- **Where to get**: [OpenAI Platform](https://platform.openai.com/api-keys)

```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

---

### MongoDB Configuration (Optional)

These variables configure the MongoDB connection. All have sensible defaults for local development.

#### MONGODB_CONNECTION_STRING
- **Description**: Full MongoDB connection string
- **Required**: No
- **Default**: `mongodb://localhost:27017/`
- **Example**: `mongodb+srv://user:pass@cluster.mongodb.net/`

**Options:**

**Local MongoDB:**
```env
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
```

**Local with Authentication:**
```env
MONGODB_CONNECTION_STRING=mongodb://username:password@localhost:27017/
```

**MongoDB Atlas (Cloud):**
```env
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

**Docker MongoDB:**
```env
MONGODB_CONNECTION_STRING=mongodb://mongodb:27017/
```

---

#### MONGODB_DATABASE_NAME
- **Description**: Name of the database to use
- **Required**: No
- **Default**: `code-interpreter-db`
- **Example**: `my-app-db`

```env
MONGODB_DATABASE_NAME=code-interpreter-db
```

**Use Cases:**
- Different databases for dev/staging/prod
- Multi-tenant applications
- Testing with separate database

---

#### MONGODB_COLLECTION_NAME
- **Description**: Collection name for storing app configuration
- **Required**: No
- **Default**: `app_config`
- **Example**: `config`

```env
MONGODB_COLLECTION_NAME=app_config
```

This collection stores:
- OpenAI Assistant ID
- Other application configuration

---

## Frontend Environment Variables

The frontend uses Vite's environment variable system. Create `frontend/.env` if needed.

### VITE_API_URL (Optional)
- **Description**: Backend API URL for production builds
- **Required**: No (uses proxy in development)
- **Default**: Uses Vite proxy configuration
- **Example**: `https://api.myapp.com`

```env
VITE_API_URL=https://api.myapp.com
```

---

## Complete .env Template

### Development (Local)

```env
# backend/.env - Development Configuration

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-dev-api-key-here

# MongoDB Configuration (Local)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=code-interpreter-dev
MONGODB_COLLECTION_NAME=app_config
```

### Production (Cloud)

```env
# backend/.env - Production Configuration

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-prod-api-key-here

# MongoDB Configuration (Atlas)
MONGODB_CONNECTION_STRING=mongodb+srv://admin:SecurePass123@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE_NAME=code-interpreter-prod
MONGODB_COLLECTION_NAME=app_config
```

---

## Environment-Specific Configurations

### Local Development
```env
OPENAI_API_KEY=sk-proj-dev-key
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=code-interpreter-dev
MONGODB_COLLECTION_NAME=app_config
```

### Staging
```env
OPENAI_API_KEY=sk-proj-staging-key
MONGODB_CONNECTION_STRING=mongodb://staging-mongo:27017/
MONGODB_DATABASE_NAME=code-interpreter-staging
MONGODB_COLLECTION_NAME=app_config
```

### Production
```env
OPENAI_API_KEY=sk-proj-prod-key
MONGODB_CONNECTION_STRING=mongodb+srv://prod-user:prod-pass@cluster.mongodb.net/
MONGODB_DATABASE_NAME=code-interpreter-prod
MONGODB_COLLECTION_NAME=app_config
```

---

## Docker Compose Environment

When using `docker-compose.yml`, you can pass environment variables:

```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGODB_CONNECTION_STRING=mongodb://mongodb:27017/
      - MONGODB_DATABASE_NAME=code-interpreter-db
      - MONGODB_COLLECTION_NAME=app_config
```

---

## Validation & Troubleshooting

### Check if variables are loaded:

**Python (Backend):**
```python
import os
from dotenv import load_dotenv

load_dotenv()

print("OPENAI_API_KEY:", "✓ Set" if os.getenv("OPENAI_API_KEY") else "✗ Missing")
print("MONGODB_CONNECTION_STRING:", os.getenv("MONGODB_CONNECTION_STRING", "Using default"))
print("MONGODB_DATABASE_NAME:", os.getenv("MONGODB_DATABASE_NAME", "Using default"))
```

### Common Issues:

**Issue: "OpenAI API key not found"**
- Solution: Check `.env` file exists in `backend/` directory
- Ensure no spaces around `=` in `.env`
- Don't use quotes around values

**Issue: "Cannot connect to MongoDB"**
- Solution: Check MongoDB is running: `docker ps` or `mongosh`
- Verify connection string format
- Check firewall/network settings

**Issue: "Environment variables not loading"**
- Solution: Make sure `python-dotenv` is installed
- Check `.env` file is in the correct directory
- Restart the backend server after changes

---

## Security Best Practices

### ✅ DO:
- Use different API keys for dev/staging/prod
- Use strong passwords for MongoDB
- Keep `.env` in `.gitignore`
- Use environment-specific configurations
- Rotate API keys periodically
- Use secrets management in production (AWS Secrets Manager, Azure Key Vault, etc.)

### ❌ DON'T:
- Commit `.env` files to git
- Share API keys in chat/email
- Use production keys in development
- Hard-code sensitive values in code
- Use default/weak MongoDB passwords

---

## Getting Help

If you're having trouble with environment variables:

1. Check the `.env.example` or `env_template.txt` files
2. Review [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. Check [MONGODB_INTEGRATION.md](MONGODB_INTEGRATION.md)
4. Create an issue with your (redacted) configuration

---

**Last Updated**: December 2025

