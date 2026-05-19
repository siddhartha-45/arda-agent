# 🚀 Push ARDA to GitHub

## Step-by-Step Instructions

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `arda-agent` or `autonomous-research-agent`
3. Description: "Autonomous Research & Decision Agent - Production-Ready Agentic AI with Jac/Jaseci"
4. Make it **Public** (for easy deployment)
5. **Do NOT** initialize with README (we have one)
6. Click "Create Repository"

### 2. Configure Git Locally

Open PowerShell in `e:\jac\arda-agent`:

```powershell
# Set git user (global)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Or local to this repo only:
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 3. Initialize Repository

```powershell
cd e:\jac\arda-agent

# Initialize git
git init

# Add all files
git add .

# Commit initial version
git commit -m "Initial ARDA deployment - Production ready autonomous research agent"

# Rename branch to main
git branch -M main
```

### 4. Add Remote & Push

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/arda-agent.git
git push -u origin main
```

### 5. Verify on GitHub

Visit: `https://github.com/YOUR_USERNAME/arda-agent`

You should see all your files!

---

## 🔐 Authentication Issues?

If you get authentication errors, use one of these methods:

### Method A: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Tokens (classic)" → "Generate new token (classic)"
3. Check `repo` and `workflow` scopes
4. Copy the token
5. When prompted for password, paste the token

### Method B: SSH Key

```powershell
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# Copy key to GitHub Settings → SSH Keys
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard

# Use SSH URL for remote
git remote set-url origin git@github.com:YOUR_USERNAME/arda-agent.git
```

### Method C: Windows Credential Manager

Windows may store credentials automatically. Try:

```powershell
# Clear stored credentials (if needed)
cmdkey /delete:git:https://github.com

# Then try pushing again - you'll be prompted for token
```

---

## 📋 Complete Command Sequence

```powershell
# Navigate to project
cd e:\jac\arda-agent

# Check git status
git status

# Configure user (if not done globally)
git config user.name "Your Name"
git config user.email "your@email.com"

# Initialize if not already done
git init

# Add all files
git add .

# Commit
git commit -m "ARDA: Production-ready autonomous research agent with Vercel deployment"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/arda-agent.git

# Push to GitHub
git push -u origin main
```

---

## ✅ Verify Push Succeeded

```powershell
# Check remote
git remote -v

# Check branches
git branch -a

# Check last commits
git log --oneline -5
```

Should show:
```
origin  https://github.com/YOUR_USERNAME/arda-agent.git (fetch)
origin  https://github.com/YOUR_USERNAME/arda-agent.git (push)
* main
```

---

## 🔄 Future Pushes

After initial setup, just use:

```powershell
git add .
git commit -m "Your commit message"
git push
```

---

## 📦 What Gets Pushed

✅ **Included:**
- Source code (main.py, tools/, jac_app/, etc.)
- Documentation (README.md, API_REFERENCE.md, etc.)
- Configuration (vercel.json, .env.example, requirements.txt)
- Web interface (public/index.html)
- Deployment files (DEPLOYMENT.md, VERCEL_DEPLOY.md)

❌ **Excluded (by .vercelignore):**
- `.git` - Git metadata
- `__pycache__` - Python cache
- `.env` - Secret keys
- `venv/` - Virtual environment
- `database/` - Local database
- `*.log` - Log files
- `node_modules/` - Dependencies

---

## 🎯 After Pushing to GitHub

1. **Deploy to Vercel:**
   - Go to https://vercel.com/new
   - Import repository
   - Auto-deploys on every push! 🚀

2. **Add README Badge:**
   ```markdown
   [![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=flat-square&logo=vercel)](https://arda-research-agent.vercel.app)
   [![GitHub](https://img.shields.io/badge/GitHub-arda--agent-blue?style=flat-square&logo=github)](https://github.com/YOUR_USERNAME/arda-agent)
   ```

3. **Setup CI/CD:**
   - Add GitHub Actions for testing
   - Automatic deployment on push

---

## 🐛 Troubleshooting

### Error: "fatal: not a git repository"
```powershell
git init
```

### Error: "refusing to merge unrelated histories"
```powershell
git pull origin main --allow-unrelated-histories
```

### Error: "Permission denied (publickey)"
- Use HTTPS instead of SSH, or
- Add SSH key to GitHub, or
- Regenerate PAT token

### Large files / Slow push
- Check file sizes: `ls -lah`
- Add to .gitignore if needed
- Use `git lfs` for large files

---

## 📚 Resources

- [GitHub Setup Guide](https://docs.github.com/en/get-started/quickstart)
- [Git Commands Reference](https://git-scm.com/docs)
- [Vercel GitHub Integration](https://vercel.com/docs/git/vercel-for-github)

---

**Ready to push? Follow the commands above! 🚀**
