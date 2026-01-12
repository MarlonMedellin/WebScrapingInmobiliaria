# Script para hacer deployment al VPS

param(
    [string]$CommitMessage = ""
)

Write-Host "Deployment al VPS" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar cambios locales
Write-Host "Paso 1: Verificando cambios locales..." -ForegroundColor Yellow
$status = git status --porcelain

if ($status) {
    Write-Host "Hay cambios sin commitear:" -ForegroundColor Red
    git status --short
    Write-Host ""
    
    if (-not $CommitMessage) {
        $CommitMessage = Read-Host "Ingresa el mensaje del commit"
    }
    
    Write-Host "Haciendo commit..." -ForegroundColor Yellow
    git add .
    git commit -m $CommitMessage
}
else {
    Write-Host "No hay cambios locales" -ForegroundColor Green
}

Write-Host ""

# 2. Push a GitHub
Write-Host "Paso 2: Pushing a GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al hacer push. Verifica tu conexion." -ForegroundColor Red
    exit 1
}

Write-Host "Push exitoso" -ForegroundColor Green
Write-Host ""

# 3. Actualizar VPS
Write-Host "Paso 3: Actualizando VPS..." -ForegroundColor Yellow
Write-Host "Ejecutando comandos en el VPS..." -ForegroundColor Gray

ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git pull origin main && docker compose restart worker backend && docker compose ps"

Write-Host ""
Write-Host "Deployment completado" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  Produccion: https://csimedellin.link" -ForegroundColor White
Write-Host "  API Docs:   https://csimedellin.link/api/docs" -ForegroundColor White
Write-Host ""
