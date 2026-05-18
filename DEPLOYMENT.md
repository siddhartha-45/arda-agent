# Deploying ARDA to Vercel

## Overview

ARDA can be deployed to Vercel as a serverless API. This guide walks through the deployment process.

**Project Name:** `arda-research-agent`  
**API Endpoint:** Will be available at `https://arda-research-agent.vercel.app`

## Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com (free tier available)
2. **Groq API Key** - Get free key at https://console.groq.com
3. **Git Repository** - Push your code to GitHub (recommended)
4. **Vercel CLI** (optional) - `npm install -g vercel`

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial ARDA deployment setup"
   git push -u origin main
   ```

2. **Import Project in Vercel**
   - Go to https://vercel.com/new
   - Select "Import Git Repository"
   - Choose your GitHub repository
   - Project Name: `arda-research-agent`
   - Framework Preset: `Other`
   - Click "Deploy"

3. **Set Environment Variables**
   - In Vercel Dashboard, go to Settings → Environment Variables
   - Add new variable:
     - Name: `GROQ_API_KEY`
     - Value: Your Groq API key
     - Environments: Production, Preview, Development
   - Click "Save"

4. **Redeploy**
   - Go to Deployments
   - Click on latest deployment
   - Click "Redeploy"

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

4. **When prompted, set environment variables**
   - Vercel CLI will ask for `GROQ_API_KEY`
   - Enter your Groq API key

### Option 3: Deploy via GitHub with Auto-Deploy

1. **Connect GitHub Repository**
   - In Vercel Dashboard: New Project → Import Git Repository
   - Select your repo and connect

2. **Enable Auto-Deployments**
   - Each push to `main` branch auto-deploys
   - Set environment variables in Vercel Dashboard

## Configuration Files

The following files enable Vercel deployment:

- **`vercel.json`** - Vercel configuration (routing, builds)
- **`api/index.py`** - Serverless function entry point
- **`.vercelignore`** - Files to exclude from deployment
- **`requirements.txt`** - Updated with `mangum>=0.17.0`

## Testing the Deployment

Once deployed, test your API:

### Health Check
```bash
curl https://arda-research-agent.vercel.app/
```

### Start Research
```bash
curl -X POST https://arda-research-agent.vercel.app/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are latest AI trends?", "depth": "standard"}'
```

### Get Info
```bash
curl https://arda-research-agent.vercel.app/api/info
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health status |
| `/research` | POST | Execute research query |
| `/api/models` | GET | Available models info |
| `/api/info` | GET | ARDA system information |

## Request/Response Examples

### Research Query
**Request:**
```json
{
  "query": "What are the latest AI developments in 2025?",
  "depth": "standard"
}
```

**Response:**
```json
{
  "session_id": "abc123def456",
  "query": "What are the latest AI developments in 2025?",
  "status": "completed",
  "findings": {
    "task_1": "Research results...",
    "task_2": "More findings..."
  },
  "recommendations": "Based on research..."
}
```

## Important Notes

### Limitations

⚠️ **Vercel Serverless Constraints:**
- **Execution Timeout**: 10 seconds (free tier)
- **Memory**: 128-3008 MB (depending on plan)
- **Persistent Storage**: Not available (database file won't persist)
- **Cold Starts**: First request may take 1-2 seconds

### Workarounds

1. **For Long-Running Queries**: 
   - Implement async processing with job queues
   - Use cron jobs for background research

2. **For Data Persistence**:
   - Integrate with PostgreSQL (e.g., Railway, Heroku Postgres)
   - Use object storage (AWS S3, Vercel Blob)

3. **For Better Performance**:
   - Consider Vercel Pro ($20/month) for longer timeouts
   - Or deploy to alternative: Railway, Render, Replit

## Monitoring & Debugging

### View Logs
```bash
vercel logs arda-research-agent
```

### Check Deployments
```bash
vercel deployments list
```

### Clear Cache
```bash
vercel remove arda-research-agent
vercel deploy --prod
```

## Upgrade Path

### Using Vercel Pro
- Longer execution times (up to 60 seconds)
- Priority support
- Cost: $20/month

### Alternative Platforms (Better for ARDA)

**Railway**
- 12 hour deployment time
- PostgreSQL included
- Persistent storage
- https://railway.app

**Render**
- Free tier available
- Background workers
- PostgreSQL + Redis
- https://render.com

**Replit**
- Python-first environment
- Full compute access
- Free tier limited
- https://replit.com

## Customization

To customize your deployment:

1. **Change Project Name**
   - Edit `vercel.json` → `projectName`
   - Current: `arda-research-agent`

2. **Add Custom Domain**
   - In Vercel Dashboard: Settings → Domains
   - Add your custom domain (e.g., arda.yourcompany.com)

3. **Set Build Commands**
   - Edit `vercel.json` → `builds`
   - Modify `@vercel/python` configuration

## Troubleshooting

### Issue: GROQ_API_KEY not found
**Solution**: Verify environment variable is set in Vercel Dashboard

### Issue: Import errors
**Solution**: Check requirements.txt includes all dependencies

### Issue: Timeout errors
**Solution**: Consider upgrading to Vercel Pro or alternative platform

### Issue: Database not persisting
**Solution**: Integrate external database (PostgreSQL, MongoDB)

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Groq API Docs**: https://console.groq.com/docs
- **ARDA GitHub**: [Your repo URL]

## Next Steps

1. ✅ Deploy API to Vercel
2. Add web frontend (React, Vue, or static HTML)
3. Implement persistent database
4. Set up monitoring & analytics
5. Add custom domain
6. Scale for production

---

**Happy Deploying! 🚀**
