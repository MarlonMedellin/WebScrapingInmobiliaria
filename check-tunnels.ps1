# Script para verificar el estado de los tuneles SSH

Write-Host "Verificando tuneles SSH..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar procesos SSH
$sshProcesses = Get-Process ssh -ErrorAction SilentlyContinue

if ($sshProcesses) {
    Write-Host "Tuneles SSH activos:" -ForegroundColor Green
    $sshProcesses | Format-Table Id, ProcessName, StartTime -AutoSize
    Write-Host ""
}
else {
    Write-Host "No se encontraron tuneles SSH activos" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para crear tuneles, ejecuta:" -ForegroundColor Yellow
    Write-Host "  ssh -L 5433:localhost:5432 vps-scraping -N -f" -ForegroundColor White
    Write-Host "  ssh -L 6380:localhost:6379 vps-scraping -N -f" -ForegroundColor White
    Write-Host ""
    exit 1
}

# 2. Verificar conectividad PostgreSQL
Write-Host "Verificando PostgreSQL (puerto 5433)..." -ForegroundColor Yellow
$pgTest = Test-NetConnection localhost -Port 5433 -WarningAction SilentlyContinue

if ($pgTest.TcpTestSucceeded) {
    Write-Host "PostgreSQL: Accesible" -ForegroundColor Green
}
else {
    Write-Host "PostgreSQL: No accesible" -ForegroundColor Red
}

Write-Host ""

# 3. Verificar conectividad Redis
Write-Host "Verificando Redis (puerto 6380)..." -ForegroundColor Yellow
$redisTest = Test-NetConnection localhost -Port 6380 -WarningAction SilentlyContinue

if ($redisTest.TcpTestSucceeded) {
    Write-Host "Redis: Accesible" -ForegroundColor Green
}
else {
    Write-Host "Redis: No accesible" -ForegroundColor Red
}

Write-Host ""

# 4. Resumen
if ($pgTest.TcpTestSucceeded -and $redisTest.TcpTestSucceeded) {
    Write-Host "Todos los tuneles funcionan correctamente" -ForegroundColor Green
}
else {
    Write-Host "Algunos tuneles no estan funcionando. Considera reiniciarlos." -ForegroundColor Yellow
}

Write-Host ""
