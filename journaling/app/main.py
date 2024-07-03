from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt

# Database connection URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1689@localhost/journaling_app"

# SQLAlchemy engine and session setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your_jwt_secret"
ALGORITHM = "HS256"

# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to fetch a user by username
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Function to create a new user
def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to authenticate a user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if user and pwd_context.verify(password, user.password):
        return user
    return None

# Function to create an access token
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# FastAPI app instance
app = FastAPI()

# Route to register a new user
@app.post("/users/")
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user = create_user(db, username, email, password)
    return user

# Route to authenticate and generate JWT token
@app.post("/token")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token}

# Main entry point when running with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

