import pytest
from httpx import AsyncClient
from main import app
import os

@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_properties_unauthenticated():
    # Endpoints de lectura son públicos (por ahora, según el plan)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/properties")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_scrape_unauthorized():
    # El scrape ahora requiere API Key
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/scrape/fincaraiz")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_scrape_authorized():
    # Usando la API Key por defecto de dev
    headers = {"X-API-Key": "dev-secret-key"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/scrape/fincaraiz", headers=headers)
    
    # Puede dar 400 si el portal no es válido, pero no 403
    assert response.status_code != 403
