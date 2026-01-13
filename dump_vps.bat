@echo off
ssh vps-scraping "docker exec -i webscrapinginmobiliaria-db-1 pg_dump -U admin realestate_db" > vps_dump_clean.sql
