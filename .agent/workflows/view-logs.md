---
description: Ver logs del entorno de desarrollo local
---

# Ver Logs de Desarrollo Local

Muestra los logs de los servicios Docker en tiempo real.

## Ver todos los logs

```powershell
docker compose -f docker-compose.local.yml logs -f
```

## Ver logs de un servicio específico

### Backend
```powershell
docker compose -f docker-compose.local.yml logs -f backend
```

### Frontend
```powershell
docker compose -f docker-compose.local.yml logs -f frontend
```

### Worker
```powershell
docker compose -f docker-compose.local.yml logs -f worker
```

## Ver últimas N líneas

```powershell
# Últimas 50 líneas del backend
docker compose -f docker-compose.local.yml logs backend --tail=50

# Últimas 100 líneas de todos los servicios
docker compose -f docker-compose.local.yml logs --tail=100
```

## Filtrar logs

```powershell
# Buscar errores en el backend
docker compose -f docker-compose.local.yml logs backend | Select-String -Pattern "error|Error|ERROR"

# Buscar logs de conexión a BD
docker compose -f docker-compose.local.yml logs backend | Select-String -Pattern "database|postgres"
```
