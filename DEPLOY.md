# Deployment Guide for Cosmic Dust Calculator

## Quick Deploy to Vercel (Recommended)

### Prerequisites
```bash
npm install -g vercel
```

### Deploy Steps

1. **Login to Vercel:**
```bash
cd cosmos_dust
vercel login
```

2. **Deploy:**
```bash
vercel
```

3. **For Production:**
```bash
vercel --prod
```

### Alternative: Deploy via GitHub

1. Push your code to GitHub (already done)
2. Go to https://vercel.com
3. Import your repository: `m123123-m/cosmos_dust`
4. Vercel will auto-detect the Flask app
5. Click Deploy

## Other Deployment Options

### Render.com

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repository: `m123123-m/cosmos_dust`
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: Python 3
5. Deploy

### Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn app:app
```

3. Deploy:
```bash
heroku create cosmos-dust-calculator
git push heroku main
```

### PythonAnywhere

1. Upload files via web interface or git
2. Configure web app to point to `app.py`
3. Set up static files mapping

## Environment Variables

No environment variables required for basic operation.

## Post-Deployment

After deployment, your app will be available at:
- Vercel: `https://cosmos-dust-xxxxx.vercel.app`
- Render: `https://cosmos-dust.onrender.com`
- Heroku: `https://cosmos-dust-calculator.herokuapp.com`

