from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from .models import Base, User
from .schemas import UserCreate, UserLogin, Token
from .auth import hash_password, verify_password, create_access_token, get_current_user


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Tracker API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print("Pwd length check: "+ str(len(user.password.encode("utf-8"))) +". Thank You.")
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password)
    )
    
    db.add(new_user)
    db.commit()
    return {"message": "User created"}


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token}

@app.get("/me")
def read_current_user(current_user: str = Depends(get_current_user)):
    return {"email": current_user}
