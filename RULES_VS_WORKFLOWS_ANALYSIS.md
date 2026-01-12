# Análisis Crítico: Rules vs Workflows vs Scripts

## 📋 RESUMEN EJECUTIVO

Después de implementar la configuración de desarrollo local, aquí está el análisis de qué debe ser **Rule**, **Workflow** o **Script**.

---

## 🎯 DEFINICIONES

### **Rules** (`.agent/rules/`)
- **Propósito**: Comportamientos automáticos que Antigravity debe seguir SIEMPRE
- **Trigger**: `always_on` - Se activan automáticamente
- **Uso**: Recordatorios, validaciones, mejores prácticas
- **Ejemplo**: "Siempre usar docker-compose.local.yml en desarrollo local"

### **Workflows** (`.agent/workflows/`)
- **Propósito**: Procedimientos paso a paso que el usuario ejecuta manualmente
- **Trigger**: Usuario invoca con `@[/nombre-workflow]`
- **Uso**: Guías detalladas, procesos complejos
- **Ejemplo**: "Cómo configurar el entorno local"

### **Scripts** (`.ps1`, `.sh`)
- **Propósito**: Automatización ejecutable
- **Trigger**: Usuario ejecuta directamente
- **Uso**: Tareas repetitivas, configuración inicial
- **Ejemplo**: `start-local-dev.ps1`

---

## 🔍 ANÁLISIS CRÍTICO: ¿QUÉ DEBE SER QUÉ?

### ✅ **DEBE SER RULE:**

#### 1. **Uso de docker-compose.local.yml**
**Por qué:** Es un comportamiento que SIEMPRE debe seguirse en local
```yaml
trigger: always_on
Cuando el usuario pida comandos Docker en local, SIEMPRE usar:
docker compose -f docker-compose.local.yml [comando]
```

#### 2. **Verificación de túneles SSH antes de errores**
**Por qué:** Evita debugging innecesario
```yaml
trigger: always_on
Antes de reportar "Connection refused" a PostgreSQL/Redis:
1. Verificar: Get-Process ssh
2. Si no hay túneles, sugerir crearlos
```

#### 3. **Recordatorio de deployment al VPS**
**Por qué:** Paso crítico que se olvida fácilmente
```yaml
trigger: always_on
Después de git push, recordar:
"No olvides actualizar el VPS con git pull y restart"
```

#### 4. **Limitación de scrapers en Docker local**
**Por qué:** Evita frustración del usuario
```yaml
trigger: always_on
Si el usuario pide ejecutar scrapers localmente:
"Los scrapers NO funcionan en Docker local. Opciones:
1. Ejecutar directamente (workflow: run-scrapers)
2. Usar el VPS"
```

---

### ✅ **DEBE SER WORKFLOW:**

#### 1. **Setup de entorno local** (`/setup-local-dev`)
**Por qué:** Proceso complejo de múltiples pasos
- Crear túneles SSH
- Configurar .env.local
- Levantar Docker Compose

#### 2. **Ejecutar scrapers directamente** (`/run-scrapers`)
**Por qué:** Requiere configuración de entorno Python
- Crear venv
- Instalar dependencias
- Configurar variables de entorno
- Ejecutar Celery

#### 3. **Ver logs** (`/view-logs`)
**Por qué:** Múltiples opciones y filtros
- Logs de todos los servicios
- Logs de servicio específico
- Filtrar por errores

#### 4. **Validar URL** (`/validar-url`)
**Por qué:** Proceso de análisis manual
- Abrir navegador
- Revisar estructura
- Documentar hallazgos

#### 5. **Git update** (`/git-update`)
**Por qué:** Secuencia de comandos git
- git status
- git add
- git commit
- git push

---

### ✅ **DEBE SER SCRIPT:**

#### 1. **`start-local-dev.ps1`**
**Por qué:** Automatiza setup completo
- Verifica túneles SSH
- Crea .env.local si no existe
- Levanta Docker Compose
- Muestra estado

#### 2. **`stop-local-dev.ps1`** (CREAR)
**Por qué:** Limpieza ordenada
```powershell
# Detener servicios Docker
docker compose -f docker-compose.local.yml down

# Cerrar túneles SSH
Get-Process ssh | Stop-Process

Write-Host "Entorno local detenido" -ForegroundColor Green
```

#### 3. **`restart-local-dev.ps1`** (CREAR)
**Por qué:** Reinicio rápido
```powershell
# Reiniciar servicios específicos
docker compose -f docker-compose.local.yml restart backend worker frontend
```

---

## 📊 MATRIZ DE DECISIÓN

| Característica | Rule | Workflow | Script |
|----------------|------|----------|--------|
| **Ejecución automática** | ✅ | ❌ | ❌ |
| **Requiere aprobación del usuario** | ❌ | ✅ | ✅ |
| **Múltiples pasos complejos** | ❌ | ✅ | ✅ |
| **Recordatorios/Validaciones** | ✅ | ❌ | ❌ |
| **Documentación de proceso** | ❌ | ✅ | ❌ |
| **Automatización completa** | ❌ | ❌ | ✅ |
| **Invocable con @[/nombre]** | ❌ | ✅ | ❌ |

---

## 🎯 RECOMENDACIONES FINALES

### **CREAR ESTOS SCRIPTS ADICIONALES:**

1. **`stop-local-dev.ps1`** - Detener todo limpiamente
2. **`restart-service.ps1`** - Reiniciar servicio específico
3. **`check-tunnels.ps1`** - Verificar estado de túneles SSH
4. **`deploy-to-vps.ps1`** - Automatizar deployment al VPS

### **CONVERTIR A RULES:**

De tu respuesta anterior, estos conceptos deben ser rules:

1. ✅ **"Siempre usar docker-compose.local.yml"**
2. ✅ **"Verificar túneles SSH antes de reportar errores"**
3. ✅ **"Recordar deployment al VPS después de push"**
4. ✅ **"Scrapers no funcionan en Docker local"**
5. ❌ **"Comandos útiles"** → Mejor como workflows o scripts
6. ❌ **"Arquitectura del sistema"** → Mejor como documentación (README)
7. ❌ **"Pasos de setup"** → Ya es workflow (/setup-local-dev)

### **NO CONVERTIR A RULES:**

- **Instrucciones paso a paso** → Workflows
- **Comandos ejecutables** → Scripts
- **Documentación técnica** → Markdown files
- **Diagramas de arquitectura** → Documentación

---

## 💡 PRINCIPIO GUÍA

**"Si Antigravity debe RECORDARLO automáticamente → Rule"**  
**"Si el usuario debe EJECUTARLO manualmente → Workflow o Script"**  
**"Si se puede AUTOMATIZAR completamente → Script"**

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Crear `local-dev.md` rule (HECHO)
2. ⏳ Crear scripts adicionales (stop, restart, check-tunnels)
3. ⏳ Actualizar documentación con referencias a workflows
4. ⏳ Crear workflow para deployment al VPS
