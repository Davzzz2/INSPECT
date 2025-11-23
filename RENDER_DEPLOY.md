# Deploy CS2 Inspect Backend to Render.com

## Quick Deploy Steps

### Option 1: Deploy from backend/ folder (Recommended)

1. **Create a GitHub repository** with the `backend/` folder
   - Push the entire `backend/` folder contents

2. **Go to Render.com**
   - Sign up/login at https://render.com
   - Click "New +" → "Web Service"

3. **Connect Repository**
   - Connect your GitHub account
   - Select the repository
   - **Root Directory**: Set to `backend` (important!)

4. **Configure Service**
   - **Name**: `cs2-inspect-backend` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn inspect_backend:app --bind 0.0.0.0:$PORT`
   - **Root Directory**: `backend`
   - **Plan**: Free tier is fine for testing

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Your service will be available at: `https://your-service-name.onrender.com`

### Option 2: Deploy entire repo (backend in subfolder)

If deploying the entire repo (with InspectPlugin folder):
- **Root Directory**: Leave empty (root)
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && gunicorn inspect_backend:app --bind 0.0.0.0:$PORT`

6. **Update Plugin**
   - Edit `InspectPlugin/InspectPlugin.cs` line 25:
     ```csharp
     private const string InspectServiceBaseUrl = "https://your-service-name.onrender.com";
     ```
   - Rebuild and deploy the plugin

## Files in backend/ folder

- `inspect_backend.py` - Main service file
- `requirements.txt` - Python dependencies
- `Procfile` - Tells Render how to start the service
- `render.yaml` - Optional Render configuration

## Testing

Once deployed, test with:
```bash
curl https://your-service-name.onrender.com/health
curl "https://your-service-name.onrender.com/?url=!g%201014642689%20639%20123%200.0758"
```

## Notes

- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- For production, consider paid tier or keep-alive service
- Service URL will be: `https://your-service-name.onrender.com`

