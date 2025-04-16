import json
import logging
import mimetypes
from argparse import ArgumentParser
from datetime import date, datetime, timezone
from urllib.parse import urlparse

import boto3
import requests

from common.logging_config import load_logging_config


def extract_apod_data(api_key: str, start_date: date, end_date: date, s3: boto3.client):
    """
    Extracts NASA Astronomy Picture of the Day (APOD) data and saves it to S3.
    :param api_key: The API key for NASA's APOD service
    :param start_date: The start date for the data extraction
    :param end_date: The end date for the data extraction
    :param s3: The S3 client for uploading data
    :return: None
    """

    logger.info(f'Extracting APOD data from {start_date} to {end_date}')

    try:
        data_request = requests.get(
            'https://api.nasa.gov/planetary/apod',
            params={
                'api_key': api_key,
                'start_date': start_date,
                'end_date': end_date,
                'thumbs': True,
            })
        data_request.raise_for_status()
        logger.info('Data request successful')
    except requests.exceptions.RequestException as e:
        logger.critical('Failed to retrieve data from NASA API', exc_info=e)
        return

    # Save full raw JSON
    full_data_key = f'apod/raw/from_{start_date}_to_{end_date}.json'
    full_data_bytes = data_request.content

    try:
        s3.put_object(
            Bucket='nasa-bronze',
            Key=full_data_key,
            Body=full_data_bytes,
            ContentType='application/json'
        )
        logger.info(f'Full raw JSON saved to s3://nasa-bronze/{full_data_key}')
    except Exception as e:
        logger.critical('Failed to save full raw JSON to S3', exc_info=e)
        return

    raw_json = data_request.json()
    logger.info(f'Extracted {len(raw_json)} entries')

    for i, entry in enumerate(raw_json, 1):
        # Save JSON entry partitioned by date
        date_str = entry.get('date')
        logger.info(f'Processing entry {i}/{len(raw_json)} for date {date_str}')

        entry_data_key = f'apod/date={date_str}/data/data.json'
        entry_data_bytes = json.dumps(entry).encode('utf-8')

        try:
            s3.put_object(
                Bucket='nasa-bronze',
                Key=entry_data_key,
                Body=entry_data_bytes,
                ContentType='application/json'
            )
            logger.info(f'Entry data saved to s3://nasa-bronze/{entry_data_key}')
        except Exception as e:
            logger.critical(f'Failed to save entry data to S3 for date {date_str}', exc_info=e)
            continue

        media_type = entry.get('media_type')
        if media_type == 'image':
            image_url = entry.get('url')
        elif media_type == 'video':
            image_url = entry.get('thumbnail_url')
        else:
            logger.warning(f'Unsupported media type {media_type} for date {date_str}')
            continue

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

        # Save image to S3 partitioned by date
        image_key = f'apod/date={date_str}/image/image.{image_extension}'
        image_bytes = image_request.content

        try:
            s3.put_object(
                Bucket='nasa-bronze',
                Key=image_key,
                Body=image_bytes,
                ContentType=image_content_type
            )
            logger.info(f'Image saved to s3://nasa-bronze/{image_key}')
        except Exception as e:
            logger.critical(f'Failed to save image to S3 for date {date_str}', exc_info=e)
            continue

    logger.info('APOD data extraction completed successfully')


if __name__ == '__main__':
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('--start_date',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d').date(),
                        default=(datetime.now(timezone.utc)).strftime('%Y-%m-%d'),
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d').date(),
                        default=(datetime.now(timezone.utc)).strftime('%Y-%m-%d'),
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--region',
                        type=str,
                        default='ap-northeast-1',
                        help='AWS region')
    parser.add_argument('--profile',
                        default='agnostk',
                        type=str,
                        help='AWS SSO Profile (only required when running locally)')
    parser.add_argument('--local',
                        action='store_true',
                        default=False,
                        help='Run locally while connecting to AWS (requires AWS SSO profile)')
    args = parser.parse_args()

    # Initialize logger
    load_logging_config()
    logger = logging.getLogger('apod_extractor')

    logger.info('Starting APOD data extraction')
    logger.info(f'Parameters: start_date={args.start_date}, end_date={args.end_date}, region={args.region}')

    # Initialize AWS session
    if args.local:
        # When running locally, use the AWS SSO profile
        boto3.setup_default_session(profile_name=args.profile)
        logger.info(f'Running in local mode with AWS SSO profile: {args.profile}')

    # Initialize AWS clients
    try:
        s3_client = boto3.client('s3', region_name=args.region)
        secrets_manager_client = boto3.client('secretsmanager', region_name=args.region)
        logger.info('AWS clients initialized successfully')

    except Exception as e:
        logger.critical('Failed to initialize AWS clients or retrieve API key', exc_info=e)
        exit(1)

    # Retrieve the API key from AWS Secrets Manager
    try:
        nasa_api_key = secrets_manager_client.get_secret_value(SecretId='nasa_API_key')['SecretString']
        logger.info('API key retrieved successfully')
    except Exception as e:
        logger.critical('Failed to retrieve API key', exc_info=e)
        exit(1)

    # Extract APOD data
    extract_apod_data(nasa_api_key, args.start_date, args.end_date, s3_client)
