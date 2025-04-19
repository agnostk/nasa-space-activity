import json
import logging
import mimetypes
from argparse import ArgumentParser
from datetime import date, datetime, timezone, timedelta
from urllib.parse import urlparse

import boto3
import requests


def extract_mars_data(api_key: str, start_date: date, end_date: date, s3: boto3.client, bucket_name: str):
    """
    Extracts NASA Rover data from the Mars API and uploads it to S3.
    :param api_key: The API key for NASA's MARS service
    :param start_date: The start date (on Earth) for the data extraction
    :param end_date: The end date (on Earth) for the data extraction
    :param s3: The S3 client for uploading data
    :param bucket_name: The S3 bucket name where data will be saved
    :return: None
    """

    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    logger.info(f'Extracting MARS data from {start_date} to {end_date}')

    for current_date in all_dates:
        try:
            logger.info(f'Processing date: {current_date}')
            data_request = requests.get(
                'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos',
                params={
                    'api_key': api_key,
                    'earth_date': current_date,
                })
            data_request.raise_for_status()
            logger.info('Data request successful')
        except requests.exceptions.RequestException as e:
            logger.critical(f'Failed to retrieve data from NASA API, skipping {current_date}.', exc_info=e)
            continue

        data_key = f'mars/date={current_date}/data/data.json'
        data_bytes = data_request.content

        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=data_key,
                Body=data_bytes,
                ContentType='application/json'
            )
            logger.info(f'Entry data saved to s3://{bucket_name}/{current_date}')
        except Exception as e:
            logger.critical(f'Failed to save entry data to S3 for date {current_date}', exc_info=e)
            continue

        raw_json = data_request.json()

        images_metadata = []

        for i, image in enumerate(raw_json.get('photos'), 1):
            logger.info(f'Processing image {i} of {len(raw_json.get("photos"))}')
            # Guess the content type of the image
            image_id = image.get('id')
            image_url = image.get('img_src')
            image_path = urlparse(image_url).path
            image_extension = image_path.split('.')[-1]
            image_content_type = mimetypes.types_map.get(f'.{image_extension}', 'application/octet-stream')

            try:
                image_request = requests.get(image_url)
                image_request.raise_for_status()
                logger.info(f'Image request successful for {image_url}')
            except requests.exceptions.RequestException as e:
                logger.critical(f'Failed to retrieve image from {image_url}', exc_info=e)
                continue

            image_key = f'mars/date={current_date}/image/image_{image_id}.{image_extension}'
            image_bytes = image_request.content

            # Save image to S3 partitioned by date
            try:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=image_key,
                    Body=image_bytes,
                    ContentType=image_content_type
                )
                logger.info(f'Image saved to s3://{bucket_name}/{image_key}')
            except Exception as e:
                logger.critical(f'Failed to save image {image_id} to S3 for date {current_date}', exc_info=e)
                continue

            metadata = {
                "id": image_id,
                "s3_path": f's3://{bucket_name}/{image_key}',
                "content_type": image_content_type,
                "image_url": image_url,
            }

            images_metadata.append(metadata)

        metadata_key = f'mars/date={current_date}/meta/images.json'

        # Convert list of images metadata into NDJSON
        lines = "\n".join(json.dumps(image) for image in images_metadata)
        images_metadata_bytes = lines.encode('utf-8')

        # Save metadata for the images
        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=metadata_key,
                Body=images_metadata_bytes,
                ContentType='application/json'
            )
            logger.info(f'Metadata saved to s3://{bucket_name}/{metadata_key}')
        except Exception as e:
            logger.critical(f'Failed to save metadata to S3 for date {current_date}', exc_info=e)
            continue

    logger.info('MARS data extraction completed successfully')


if __name__ == '__main__':
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('--start_date',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d').date(),
                        default=(datetime.now(timezone.utc)).strftime('%Y-%m-%d'),
                        help='Start date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--end_date',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d').date(),
                        default=(datetime.now(timezone.utc)).strftime('%Y-%m-%d'),
                        help='End date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--nasa_secret_key',
                        type=str,
                        help='AWS Secrets Manager key for NASA API key',
                        required=True)
    parser.add_argument('--bronze_bucket_key',
                        type=str,
                        help='AWS S3 bucket key for bronze data',
                        required=True)
    args, _ = parser.parse_known_args()

    # Initialize logger
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    logger.info('Starting MARS data extraction')
    logger.info(f'Parameters: start_date={args.start_date}, end_date={args.end_date}')

    # Initialize AWS clients
    try:
        s3_client = boto3.client('s3')
        secrets_manager_client = boto3.client('secretsmanager')
        logger.info('AWS clients initialized successfully')
    except Exception as e:
        logger.critical('Failed to initialize AWS clients', exc_info=e)
        exit(1)

    # Retrieve the API key from AWS Secrets Manager
    try:
        nasa_api_key = secrets_manager_client.get_secret_value(
            SecretId=args.nasa_secret_key
        )['SecretString']
        logger.info('API key retrieved successfully')
    except Exception as e:
        logger.critical('Failed to retrieve API key', exc_info=e)
        exit(1)

    # Extract MARS data
    extract_mars_data(
        api_key=nasa_api_key,
        start_date=args.start_date,
        end_date=args.end_date,
        s3=s3_client,
        bucket_name=args.bronze_bucket_key
    )
