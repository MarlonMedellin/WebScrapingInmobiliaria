---
description: Sincronizar mapa de barrios entre LOCAL <-> VPS
---

# 🔄 Sincronización Completa del Mapa de Barrios

Este workflow reconcilia los barrios descubiertos, ejecuta la limpieza de Fase 3 y asegura que tanto local como VPS tengan la misma versión del mapa.

// turbo
# 1. Ejecutar limpieza y auto-mapeo masivo en el VPS (Fase 3)
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git pull origin main && python3 backend/sync_neighborhoods.py"

# 2. Subir cambios del VPS a GitHub
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git add backend/neighborhood_map.json backend/discovered_neighborhoods.json && git commit -m '🤖 [Sync] Actualización automática de mapa de barrios' || echo 'No changes'"
ssh vps-scraping "cd /root/WebScrapingInmobiliaria && git push origin main || echo 'Nothing to push'"

# 3. Traer cambios al entorno Local
git pull origin main

# 4. Confirmar estado
echo "✅ El mapa de barrios ha sido sincronizado. Local y VPS están en sintonía."
