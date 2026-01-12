---
description: actualizacion del repo
---

revisa los cambios realizados
escribe un comentario para github

# 1. En tu máquina local:
git add .
git commit -m "descripción del cambio"
git push origin main
# 2. En el VPS:
ssh vps-scraping
cd /root/WebScrapingInmobiliaria
git pull origin main
docker compose restart worker  # Si cambias scrapers/backend
docker compose restart backend # Si cambias API
docker compose restart frontend # Si cambias React
# 3. Verificar:
docker compose ps  # Ver que todos estén "Up"