# GPU Detector - Deployment Guide

This guide will help you deploy your GPU Detector app to various platforms.

## Quick Deploy Options

### 1. Render (Recommended - Free)

1. **Fork/Upload to GitHub**
   - Push your code to a GitHub repository

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New Web Service"
   - Connect your GitHub repo
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`
   - Choose free plan
   - Deploy!

### 2. Railway (Free Tier)

1. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect it's a Python app
   - Deploy!

### 3. Vercel (Free)

1. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Import your repository
   - Vercel will auto-detect Python
   - Deploy!

### 4. Heroku (Paid)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   ```

2. **Deploy**
   ```bash
   heroku login
   heroku create your-gpu-detector-app
   git add .
   git commit -m "Ready for deployment"
   git push heroku main
   ```

## Environment Variables

For production, you might want to set:
- `FLASK_ENV=production`
- `PORT=8080` (some platforms set this automatically)

## Testing Your Deployment

After deployment, test these endpoints:
- `https://your-app-url.com/` - Main page
- `https://your-app-url.com/api/detect` - API endpoint
- `https://your-app-url.com/api/health` - Health check

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Port Issues**: Some platforms set PORT environment variable
3. **Timeout**: GPU detection might timeout on some platforms

### Debug Mode:
- Set `FLASK_ENV=development` for debug output
- Check platform logs for error messages

## Security Notes

- The app doesn't store any user data
- All detection happens client-side
- No sensitive information is transmitted

## Performance

- The app is lightweight and should work well on free tiers
- GPU detection might be slower on some platforms
- Consider adding caching if you get high traffic
