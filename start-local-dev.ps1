# Script para configurar y levantar el entorno de desarrollo local
# Conectado a la base de datos del VPS

Write-Host "Configurando entorno de desarrollo local conectado a VPS..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar si existen los tuneles SSH
Write-Host "Paso 1: Verificando tuneles SSH..." -ForegroundColor Yellow
$sshProcesses = Get-Process ssh -ErrorAction SilentlyContinue

if ($sshProcesses) {
    Write-Host "Tuneles SSH activos encontrados:" -ForegroundColor Green
    $sshProcesses | Format-Table Id, ProcessName, StartTime -AutoSize
}
else {
    Write-Host "No se encontraron tuneles SSH activos" -ForegroundColor Red
    Write-Host "Creando tuneles SSH..." -ForegroundColor Yellow
    
    # Crear tunel para PostgreSQL
    Start-Process -FilePath "ssh" -ArgumentList "-L 5433:localhost:5432 vps-scraping -N" -WindowStyle Hidden
    Write-Host "  Tunel PostgreSQL: 5433 -> VPS:5432" -ForegroundColor Green
    
    # Crear tunel para Redis
    Start-Process -FilePath "ssh" -ArgumentList "-L 6380:localhost:6379 vps-scraping -N" -WindowStyle Hidden
    Write-Host "  Tunel Redis: 6380 -> VPS:6379" -ForegroundColor Green
    
    Start-Sleep -Seconds 2
}

Write-Host ""

# 2. Verificar archivo .env.local
Write-Host "Paso 2: Verificando archivo .env.local..." -ForegroundColor Yellow

if (Test-Path ".env.local") {
    Write-Host "Archivo .env.local encontrado" -ForegroundColor Green
}
else {
    Write-Host "Creando archivo .env.local..." -ForegroundColor Yellow
    
    $envContent = @"
# Configuracion para desarrollo local conectado a VPS
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=realestate_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

REDIS_URL=redis://localhost:6380/0

VITE_API_BASE_URL=http://localhost:8000
"@
    
    $envContent | Out-File -FilePath ".env.local" -Encoding utf8
    Write-Host "Archivo .env.local creado" -ForegroundColor Green
}

Write-Host ""

# 3. Levantar servicios con Docker Compose
Write-Host "Paso 3: Levantando servicios Docker..." -ForegroundColor Yellow
Write-Host "Ejecutando: docker compose -f docker-compose.local.yml up -d" -ForegroundColor Gray

docker compose -f docker-compose.local.yml up -d

Write-Host ""

# 4. Verificar estado de servicios
Write-Host "Paso 4: Verificando estado de servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

docker compose -f docker-compose.local.yml ps

Write-Host ""
Write-Host "Entorno de desarrollo local configurado!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "   Ver logs:        docker compose -f docker-compose.local.yml logs -f" -ForegroundColor White
Write-Host "   Detener:         docker compose -f docker-compose.local.yml down" -ForegroundColor White
Write-Host "   Reiniciar:       docker compose -f docker-compose.local.yml restart" -ForegroundColor White
Write-Host "   Cerrar tuneles:  Get-Process ssh | Stop-Process" -ForegroundColor White
Write-Host ""
