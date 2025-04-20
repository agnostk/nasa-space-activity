from os import environ

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, Float, Date, Text, String, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

load_dotenv()

POSTGRES_USER = environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = environ.get('POSTGRES_HOST')
POSTGRES_PORT = environ.get('POSTGRES_PORT')
POSTGRES_DB = environ.get('POSTGRES_DB')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()


# Table Definitions

class NasaApodData(Base):
    __tablename__ = 'apod'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    title = Column(Text)
    copyright = Column(Text)
    explanation = Column(Text)
    media_type = Column(Text)
    image_url = Column(Text)
    s3_path = Column(Text)
    average_color_r = Column(Integer)
    average_color_g = Column(Integer)
    average_color_b = Column(Integer)
    image_hash = Column(Text)
    classification = Column(Text)
    classification_confidence = Column(Float)
    image_width = Column(Integer)
    image_height = Column(Integer)


class NasaMarsData(Base):
    __tablename__ = 'mars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    photo_id = Column(Integer)
    sol = Column(Integer)
    camera_id = Column(Integer)
    camera_full_name = Column(Text)
    img_src = Column(Text)
    rover_name = Column(Text)
    rover_status = Column(Text)
    s3_path = Column(Text)
    average_color_r = Column(Integer)
    average_color_g = Column(Integer)
    average_color_b = Column(Integer)
    image_hash = Column(Text)
    classification = Column(Text)
    classification_confidence = Column(Float)
    image_width = Column(Integer)
    image_height = Column(Integer)


class NasaNeoData(Base):
    __tablename__ = 'neo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    asteroid_id = Column(String)
    asteroid_name = Column(String)
    absolute_magnitude_h = Column(Float)
    diameter_min_km = Column(Float)
    diameter_max_km = Column(Float)
    hazardous = Column(Boolean)
    close_approach_date = Column(String)
    velocity_kph = Column(Float)
    miss_distance_km = Column(Float)
    orbiting_body = Column(String)
    is_sentry_object = Column(Boolean)
    sentry_data = Column(Text)
    threat_score = Column(Float)


# Create Tables
Base.metadata.create_all(engine)

# Create Unified View
create_view_sql = text("""
CREATE OR REPLACE VIEW public.nasa_unified_view AS
SELECT
    'apod' AS source,
    id,
    date,
    title,
    copyright,
    explanation,
    media_type,
    image_url,
    NULL::integer AS photo_id,
    NULL::integer AS sol,
    NULL::integer AS camera_id,
    NULL::text AS camera_full_name,
    NULL::text AS img_src,
    NULL::text AS rover_name,
    NULL::text AS rover_status,
    s3_path,
    average_color_r,
    average_color_g,
    average_color_b,
    image_hash,
    classification,
    classification_confidence,
    image_width,
    image_height,
    NULL::text AS asteroid_id,
    NULL::text AS asteroid_name,
    NULL::double precision AS absolute_magnitude_h,
    NULL::double precision AS diameter_min_km,
    NULL::double precision AS diameter_max_km,
    NULL::boolean AS hazardous,
    NULL::text AS close_approach_date,
    NULL::double precision AS velocity_kph,
    NULL::double precision AS miss_distance_km,
    NULL::text AS orbiting_body,
    NULL::boolean AS is_sentry_object,
    NULL::text AS sentry_data,
    NULL::double precision AS threat_score
FROM public.apod

UNION ALL

SELECT
    'mars' AS source,
    id,
    date,
    NULL::text AS title,
    NULL::text AS copyright,
    NULL::text AS explanation,
    NULL::text AS media_type,
    NULL::text AS image_url,
    photo_id,
    sol,
    camera_id,
    camera_full_name,
    img_src,
    rover_name,
    rover_status,
    s3_path,
    average_color_r,
    average_color_g,
    average_color_b,
    image_hash,
    classification,
    classification_confidence,
    image_width,
    image_height,
    NULL::text AS asteroid_id,
    NULL::text AS asteroid_name,
    NULL::double precision AS absolute_magnitude_h,
    NULL::double precision AS diameter_min_km,
    NULL::double precision AS diameter_max_km,
    NULL::boolean AS hazardous,
    NULL::text AS close_approach_date,
    NULL::double precision AS velocity_kph,
    NULL::double precision AS miss_distance_km,
    NULL::text AS orbiting_body,
    NULL::boolean AS is_sentry_object,
    NULL::text AS sentry_data,
    NULL::double precision AS threat_score
FROM public.mars

UNION ALL

SELECT
    'neo' AS source,
    id,
    date,
    NULL::text AS title,
    NULL::text AS copyright,
    NULL::text AS explanation,
    NULL::text AS media_type,
    NULL::text AS image_url,
    NULL::integer AS photo_id,
    NULL::integer AS sol,
    NULL::integer AS camera_id,
    NULL::text AS camera_full_name,
    NULL::text AS img_src,
    NULL::text AS rover_name,
    NULL::text AS rover_status,
    NULL::text AS s3_path,
    NULL::integer AS average_color_r,
    NULL::integer AS average_color_g,
    NULL::integer AS average_color_b,
    NULL::text AS image_hash,
    NULL::text AS classification,
    NULL::double precision AS classification_confidence,
    NULL::integer AS image_width,
    NULL::integer AS image_height,
    asteroid_id,
    asteroid_name,
    absolute_magnitude_h,
    diameter_min_km,
    diameter_max_km,
    hazardous,
    close_approach_date,
    velocity_kph,
    miss_distance_km,
    orbiting_body,
    is_sentry_object,
    sentry_data,
    threat_score
FROM public.neo;
""")

# Created Materialized View For Mosaic
create_materialized_view_sql = text("""
CREATE MATERIALIZED VIEW public.nasa_image_pool AS
SELECT
    'apod' AS source,
    id,
    date,
    s3_path,
    image_url,
    average_color_r,
    average_color_g,
    average_color_b,
    classification,
    image_width,
    image_height
FROM public.apod

UNION ALL

SELECT
    'mars' AS source,
    id,
    date,
    s3_path,
    img_src AS image_url,
    average_color_r,
    average_color_g,
    average_color_b,
    classification,
    image_width,
    image_height
FROM public.mars;
""")

add_mosaic_index_sql = text("""
CREATE INDEX idx_nasa_image_pool_rgb
ON public.nasa_image_pool (average_color_r, average_color_g, average_color_b);
""")

with engine.connect() as conn:
    conn.execute(create_view_sql)
    conn.commit()
