@echo off
echo [1/4] Dumping local database...
docker exec -i local_postgres_dump pg_dump -U admin -Fc realestate_db > local_full.dump

echo [2/4] Uploading dump to VPS...
scp local_full.dump vps-scraping:/tmp/local_full.dump

echo [3/4] Copying to container...
ssh vps-scraping "docker cp /tmp/local_full.dump webscrapinginmobiliaria-db-1:/tmp/local_full.dump"

echo [4/4] Restoring to VPS Database...
ssh vps-scraping "docker exec -i webscrapinginmobiliaria-db-1 pg_restore -U admin -d realestate_db --clean --if-exists /tmp/local_full.dump"

echo Done!
