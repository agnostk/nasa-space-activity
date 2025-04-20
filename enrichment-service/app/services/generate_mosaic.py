from io import BytesIO
from typing import List

import numpy as np
import psycopg2
from PIL import Image
from fastapi import UploadFile

from app.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from app.models import MosaicTile, RGBColor

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}


def resize_image(image: UploadFile, width: int, height: int) -> np.ndarray:
    img = Image.open(BytesIO(image.file.read())).convert("RGB")
    img = img.resize((width, height))
    return np.array(img).reshape((width * height, 3))


def fetch_all_images(cursor):
    cursor.execute("""
        SELECT source, id, date, s3_path, image_url,
               average_color_r, average_color_g, average_color_b, classification
        FROM nasa_image_pool
        WHERE average_color_r IS NOT NULL
          AND average_color_g IS NOT NULL
          AND average_color_b IS NOT NULL
    """)
    rows = cursor.fetchall()
    tiles = []
    colors = []

    for row in rows:
        r, g, b = int(row[5]), int(row[6]), int(row[7])
        tiles.append(MosaicTile(
            source=row[0],
            id=str(row[1]),
            date=str(row[2]),
            s3_path=row[3],
            image_url=row[4],
            average_color=RGBColor(r=r, g=g, b=b),
            classification=row[8],
        ))
        colors.append((r, g, b))

    return tiles, np.array(colors)


def generate_mosaic(image: UploadFile, mosaic_size: int) -> dict:
    pixels = resize_image(image, mosaic_size, mosaic_size)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    all_tiles, color_vectors = fetch_all_images(cur)

    distances = np.linalg.norm(pixels[:, np.newaxis] - color_vectors, axis=2)
    best_indices = np.argmin(distances, axis=1)

    mosaic_tiles: List[MosaicTile] = [all_tiles[i] for i in best_indices]

    cur.close()
    conn.close()

    return {"mosaic_tiles": mosaic_tiles}
