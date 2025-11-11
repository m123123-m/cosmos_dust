# Deployment Guide

## Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the web interface:**
Open your browser to `http://localhost:5000`

## GitHub Deployment

### Initial Setup

1. **Initialize git repository (if not already done):**
```bash
git init
```

2. **Add GitHub remote:**
```bash
git remote add origin https://github.com/m123123-m/cosmos_dust.git
```

3. **Add and commit files:**
```bash
git add .
git commit -m "Initial commit: Cosmic Dust Trajectory Calculator"
```

4. **Push to GitHub:**
```bash
git branch -M main
git push -u origin main
```

Or use the provided script:
```bash
./setup_github.sh
```

## Deployment Options

### Option 1: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn app:app
```

3. Deploy:
```bash
heroku create
git push heroku main
```

### Option 2: PythonAnywhere

1. Upload files via web interface or git
2. Configure web app to point to `app.py`
3. Set up static files mapping

### Option 3: Vercel (Serverless)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel
```

### Option 4: Docker

1. Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

2. Build and run:
```bash
docker build -t cosmos-dust .
docker run -p 5000:5000 cosmos-dust
```

## Environment Variables

No environment variables are required for basic operation. The application uses default parameters that can be configured through the web interface.

## Production Considerations

1. **Use a production WSGI server:**
   - Gunicorn: `gunicorn app:app`
   - Waitress: `waitress-serve --port=5000 app:app`

2. **Set up proper logging:**
   - Configure Flask logging for production
   - Set up error tracking (Sentry, etc.)

3. **Optimize for large simulations:**
   - Consider background job processing (Celery, RQ)
   - Add caching for repeated simulations
   - Implement result pagination

4. **Security:**
   - Set `FLASK_ENV=production`
   - Use proper secret keys
   - Implement rate limiting
   - Add CORS restrictions if needed

