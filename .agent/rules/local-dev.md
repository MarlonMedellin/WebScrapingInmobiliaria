---
trigger: always_on
glob:
description: Reglas para desarrollo local del proyecto WebScrapingInmobiliaria
---

# Reglas de Desarrollo Local

## Entorno de Desarrollo

Cuando el usuario trabaje en desarrollo local:

1. **Siempre usar docker-compose.local.yml** para comandos Docker
2. **Verificar tuneles SSH** antes de levantar servicios
3. **Recordar que los scrapers NO funcionan en Docker local** - sugerir ejecutarlos directamente o en el VPS

## Deployment al VPS

Despues de cada commit y push a GitHub, recordar al usuario:

ssh vps-scraping
cd /root/WebScrapingInmobiliaria
git pull origin main
docker compose restart worker backend

## Verificacion de Conexiones

Antes de reportar errores de conexion, verificar:
- Tuneles SSH activos: Get-Process ssh
- PostgreSQL accesible: Test-NetConnection localhost -Port 5433
- Redis accesible: Test-NetConnection localhost -Port 6380

## Comandos Frecuentes

Cuando el usuario pida ver logs, usar:
docker compose -f docker-compose.local.yml logs -f

Cuando el usuario pida reiniciar, preguntar que servicio y usar:
docker compose -f docker-compose.local.yml restart [servicio]

Cuando el usuario pida detener todo, usar:
docker compose -f docker-compose.local.yml down
