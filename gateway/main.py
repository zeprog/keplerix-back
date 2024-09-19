from fastapi import FastAPI, Request
import httpx

app = FastAPI()

USER_SERVICE_URL = "http://user-service:8000"
FILE_SERVICE_URL = "http://file-service:8001"

@app.get("/users/{path:path}")
async def proxy_user_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/{path}", headers=request.headers)
        return response.json()

@app.post("/users/{path:path}")
async def proxy_user_service_post(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/{path}", json=await request.json(), headers=request.headers)
        return response.json()
    
@app.patch("/users/{path:path}")
async def proxy_user_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/{path}", headers=request.headers)
        return response.json()
    
@app.delete("/users/{path:path}")
async def proxy_user_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/{path}", headers=request.headers)
        return response.json()

@app.get("/files/{path:path}")
async def proxy_file_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FILE_SERVICE_URL}/{path}", headers=request.headers)
        return response.json()

@app.post("/files/{path:path}")
async def proxy_file_service_post(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FILE_SERVICE_URL}/{path}", json=await request.json(), headers=request.headers)
        return response.json()