from os import environ

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

POSTGRES_USER = environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = environ.get('POSTGRES_HOST')
POSTGRES_PORT = environ.get('POSTGRES_PORT')
POSTGRES_DB = environ.get('POSTGRES_DB')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()


class NasaEnrichedData(Base):
    __tablename__ = 'apod'

    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ Required primary key

    title = Column(Text)
    copyright = Column(Text)
    explanation = Column(Text)
    media_type = Column(Text)
    url = Column(Text)
    s3_path = Column(Text)
    date = Column(Date)

    average_color_r = Column(Integer)
    average_color_g = Column(Integer)
    average_color_b = Column(Integer)
    image_hash = Column(Text)
    classification = Column(Text)
    classification_confidence = Column(Float)
    image_width = Column(Integer)
    image_height = Column(Integer)


# Create table if it doesn't exist
Base.metadata.create_all(engine)
