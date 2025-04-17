from PIL import Image
import requests
import imagehash
from io import BytesIO
import mimetypes


def analyze_image(image_url: str):
    # Download image
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    # Load image
    img = Image.open(BytesIO(response.content)).convert('RGB')

    # Size and content type
    width, height = img.size
    content_type = response.headers.get('Content-Type') or mimetypes.guess_type(image_url)[0]

    # Average color
    pixels = list(img.getdata())
    num_pixels = len(pixels)
    avg_r = sum(p[0] for p in pixels) // num_pixels
    avg_g = sum(p[1] for p in pixels) // num_pixels
    avg_b = sum(p[2] for p in pixels) // num_pixels

    # Image hash
    phash = str(imagehash.phash(img))

    return {
        'average_color': {'r': avg_r, 'g': avg_g, 'b': avg_b},
        'image_hash': phash,
        'width': width,
        'height': height,
        'content_type': content_type
    }
