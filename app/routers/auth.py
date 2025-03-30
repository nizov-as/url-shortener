from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, auth
from app.database import SessionLocal
from starlette.status import HTTP_201_CREATED
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import Token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/register", response_model=schemas.UserResponse, status_code=HTTP_201_CREATED)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_user = await auth.create_user(db, user)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

