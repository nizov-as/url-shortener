from fastapi import FastAPI
from app.routers import links, auth as auth_router

app = FastAPI()

app.include_router(links.router)
app.include_router(auth_router.router)

@app.get("/")
def read_root():
    return {"message": "URL Shortener is alive!"}
