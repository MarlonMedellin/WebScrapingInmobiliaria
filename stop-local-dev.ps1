# Script para detener el entorno de desarrollo local

Write-Host "Deteniendo entorno de desarrollo local..." -ForegroundColor Cyan
Write-Host ""

# 1. Detener servicios Docker
Write-Host "Paso 1: Deteniendo servicios Docker..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml down

Write-Host ""

# 2. Cerrar tuneles SSH
Write-Host "Paso 2: Cerrando tuneles SSH..." -ForegroundColor Yellow
$sshProcesses = Get-Process ssh -ErrorAction SilentlyContinue

if ($sshProcesses) {
    $sshProcesses | Stop-Process
    Write-Host "Tuneles SSH cerrados" -ForegroundColor Green
}
else {
    Write-Host "No se encontraron tuneles SSH activos" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Entorno local detenido correctamente" -ForegroundColor Green
Write-Host ""
