from sqlalchemy import Column, Integer, Float, String, Date, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
from passlib.context import CryptContext

# -------------------- DATABASE SETUP --------------------
DATABASE_URL = "sqlite:///./life_analytics.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------- ENTRY MODEL --------------------
class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today)
    sleep_hours = Column(Float)
    mood = Column(Integer)
    productivity = Column(Integer)

# -------------------- USER MODEL (STEP 5.2) --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# -------------------- PASSWORD HELPERS --------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# -------------------- INIT DATABASE --------------------
def init_db():
    Base.metadata.create_all(bind=engine)
