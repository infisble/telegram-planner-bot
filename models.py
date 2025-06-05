from sqlalchemy import Column, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)  # ID может быть большим числом (например, Telegram user_id)
    telegram_id = Column(BigInteger, unique=True, nullable=False)  # Telegram ID — уникальный
    phone = Column(String, nullable=True)  # Телефон — можно оставить пустым
