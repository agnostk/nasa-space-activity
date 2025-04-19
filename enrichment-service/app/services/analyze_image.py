from io import BytesIO

import boto3
import imagehash
import requests
from PIL import Image

from app.services.classify_image import classify_image


def analyze_image(image_source: str, is_s3: bool = False):
    """
    Analyzes an image from a URL or S3 path.
    If `is_s3` is True, `image_source` is treated as an S3 URI: 's3://bucket/key'.
    """
    if is_s3:
        # Parse the S3 path
        if not image_source.startswith("s3://"):
            raise ValueError("S3 path must start with s3://")

        s3_parts = image_source[5:].split("/", 1)
        if len(s3_parts) != 2:
            raise ValueError("Invalid S3 URI format, must be s3://bucket/key")

        bucket, key = s3_parts
        s3 = boto3.client("s3")
        s3_response = s3.get_object(Bucket=bucket, Key=key)
        image_data = s3_response["Body"].read()
    else:
        response = requests.get(image_source, timeout=10)
        response.raise_for_status()
        image_data = response.content

    # Load image
    img = Image.open(BytesIO(image_data)).convert("RGB")

    # Size
    width, height = img.size

    # Average color
    pixels = list(img.getdata())
    num_pixels = len(pixels)
    avg_r = sum(p[0] for p in pixels) // num_pixels
    avg_g = sum(p[1] for p in pixels) // num_pixels
    avg_b = sum(p[2] for p in pixels) // num_pixels

    # Image hash
    phash = str(imagehash.phash(img))

    try:
        classification = classify_image(img)
    except Exception as e:
        classification = None
        print(f"Classification failed: {str(e)}")

    return {
        "average_color": {"r": avg_r, "g": avg_g, "b": avg_b},
        "image_hash": phash,
        "width": width,
        "height": height,
        "classification": classification,
    }
