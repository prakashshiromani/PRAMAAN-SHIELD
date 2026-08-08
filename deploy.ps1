# PRAMAAN-SHIELD — HuggingFace Spaces Deployment Script
# Run this from: C:\Users\Prakash Max\OneDrive\Desktop\sbi project\
# Requirements: git + huggingface_hub installed

# ============================================================
# STEP 1: Main GitHub Repo Push (code + frontend)
# ============================================================
Write-Host "=== STEP 1: Pushing main repo to GitHub ===" -ForegroundColor Green

git init
git add .
git commit -m "PRAMAAN-SHIELD: SEBI TechSprint 2026 - Team Black Ghost"

# Replace YOUR_GITHUB_USERNAME below
$GITHUB_USER = "YOUR_GITHUB_USERNAME"
git remote add origin "https://github.com/$GITHUB_USER/pramaan-shield.git"
git push -u origin main

Write-Host "GitHub repo pushed!" -ForegroundColor Green

# ============================================================
# STEP 2: HuggingFace Spaces — Backend Deployment
# HF Spaces needs a SEPARATE repo with Dockerfile at root
# ============================================================
Write-Host "=== STEP 2: Setting up HuggingFace Spaces ===" -ForegroundColor Cyan

# Create a temp folder for HF deployment
$HF_DIR = "$env:TEMP\pramaan-hf-space"
New-Item -ItemType Directory -Force -Path $HF_DIR

# Copy backend files to HF folder
Copy-Item -Path "backend\app" -Destination "$HF_DIR\app" -Recurse -Force
Copy-Item -Path "backend\requirements-hf.txt" -Destination "$HF_DIR\requirements-hf.txt"
Copy-Item -Path "backend\Dockerfile.hf" -Destination "$HF_DIR\Dockerfile"
Copy-Item -Path "backend\README.md" -Destination "$HF_DIR\README.md"

Write-Host "HF files prepared at $HF_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "=== NEXT: Go to https://huggingface.co/new-space ===" -ForegroundColor Yellow
Write-Host "1. Space name: pramaan-shield" -ForegroundColor Yellow
Write-Host "2. SDK: Docker" -ForegroundColor Yellow
Write-Host "3. Visibility: Public" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then run in $HF_DIR :" -ForegroundColor Yellow
Write-Host "   git init" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor White
Write-Host "   git commit -m 'PRAMAAN-SHIELD backend'" -ForegroundColor White
Write-Host "   git remote add space https://huggingface.co/spaces/YOUR_HF_USERNAME/pramaan-shield" -ForegroundColor White
Write-Host "   git push space main" -ForegroundColor White
