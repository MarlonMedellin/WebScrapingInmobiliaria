# Scripts de Desarrollo Local

Colección de scripts PowerShell para facilitar el desarrollo local del proyecto.

## 📋 Scripts Disponibles

### 🚀 `start-local-dev.ps1`
Inicia el entorno de desarrollo local completo.

**Qué hace:**
- ✅ Verifica/crea túneles SSH al VPS
- ✅ Crea archivo `.env.local` si no existe
- ✅ Levanta servicios Docker (backend, frontend, worker)
- ✅ Muestra estado de servicios

**Uso:**
```powershell
.\start-local-dev.ps1
```

---

### 🛑 `stop-local-dev.ps1`
Detiene el entorno de desarrollo local.

**Qué hace:**
- ✅ Detiene servicios Docker
- ✅ Cierra túneles SSH

**Uso:**
```powershell
.\stop-local-dev.ps1
```

---

### 🔍 `check-tunnels.ps1`
Verifica el estado de los túneles SSH.

**Qué hace:**
- ✅ Lista procesos SSH activos
- ✅ Verifica conectividad a PostgreSQL (puerto 5433)
- ✅ Verifica conectividad a Redis (puerto 6380)
- ✅ Muestra resumen de estado

**Uso:**
```powershell
.\check-tunnels.ps1
```

**Salida esperada:**
```
Tuneles SSH activos:
Id    ProcessName StartTime
--    ----------- ---------
12345 ssh         12/01/2026 9:00:00 AM
67890 ssh         12/01/2026 9:00:01 AM

PostgreSQL: Accesible ✓
Redis: Accesible ✓

Todos los tuneles funcionan correctamente
```

---

### 🚢 `deploy-to-vps.ps1`
Automatiza el deployment completo al VPS.

**Qué hace:**
- ✅ Verifica cambios locales
- ✅ Hace commit (si hay cambios)
- ✅ Push a GitHub
- ✅ Pull en el VPS
- ✅ Reinicia servicios en el VPS
- ✅ Muestra estado final

**Uso:**
```powershell
# Con mensaje de commit
.\deploy-to-vps.ps1 -CommitMessage "Fix: corregir bug en scraper"

# Sin mensaje (te pedirá uno si hay cambios)
.\deploy-to-vps.ps1
```

**Flujo completo:**
```
Local → GitHub → VPS
  ↓       ↓       ↓
commit  push   pull + restart
```

---

## 🔄 Workflows Disponibles

### `/setup-local-dev`
Guía paso a paso para configurar el entorno local por primera vez.

### `/run-scrapers`
Instrucciones para ejecutar scrapers directamente (sin Docker).

### `/view-logs`
Comandos para ver logs de los servicios.

### `/git-update`
Proceso para actualizar el repositorio.

### `/validar-url`
Validar URLs de portales inmobiliarios.

---

## 📚 Documentación Adicional

- **`LOCAL_DEV.md`** - Guía completa de desarrollo local
- **`RULES_VS_WORKFLOWS_ANALYSIS.md`** - Análisis de arquitectura de automatización
- **`README.md`** - Documentación general del proyecto

---

## 🎯 Flujo de Trabajo Típico

### Inicio del día:
```powershell
# 1. Iniciar entorno local
.\start-local-dev.ps1

# 2. Verificar que todo funciona
.\check-tunnels.ps1

# 3. Abrir frontend
# http://localhost:5173
```

### Durante el desarrollo:
```powershell
# Ver logs en tiempo real
docker compose -f docker-compose.local.yml logs -f backend

# Reiniciar un servicio
docker compose -f docker-compose.local.yml restart backend
```

### Al finalizar el día:
```powershell
# 1. Hacer deployment al VPS
.\deploy-to-vps.ps1 -CommitMessage "feat: nueva funcionalidad"

# 2. Detener entorno local
.\stop-local-dev.ps1
```

---

## ⚠️ Troubleshooting

### Error: "Cannot connect to Docker"
**Solución:** Asegúrate de que Docker Desktop esté corriendo.

### Error: "Connection refused" a PostgreSQL/Redis
**Solución:** 
```powershell
.\check-tunnels.ps1
# Si no hay túneles, ejecuta:
.\start-local-dev.ps1
```

### Los scrapers no funcionan en Docker local
**Solución:** Usa el workflow `/run-scrapers` para ejecutarlos directamente.

---

## 🔐 Seguridad

- ✅ Los archivos `.env.local` están en `.gitignore`
- ✅ Los túneles SSH usan autenticación por clave
- ✅ Las credenciales nunca se commitean

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa `LOCAL_DEV.md` para troubleshooting detallado
2. Ejecuta `.\check-tunnels.ps1` para diagnóstico
3. Revisa los logs: `docker compose -f docker-compose.local.yml logs`
