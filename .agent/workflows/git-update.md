---
description: actualizacion del repo con proteccion de mapeo
---

# Flujo de Actualización con Seguridad de Datos

Este flujo asegura que los barrios auto-aprendidos por el servidor no se pierdan al subir cambios locales.

// turbo
# 1. Traer cambios del servidor (MUY IMPORTANTE)
# El servidor puede haber aprendido barrios nuevos vía frontend.
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git add backend/neighborhood_map.json && git commit -m 'Auto-map update from server' || echo 'No new maps'"
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git push origin main || echo 'Nothing to push'"
git pull origin main

# 2. En tu máquina local:
git add .
git commit -m "descripción del cambio"
git push origin main

# 3. Desplegar al VPS:
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git pull origin main && docker compose restart worker backend"

# 4. Verificar:
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && docker compose ps"