import json
import logging
from argparse import ArgumentParser
from datetime import date, datetime, timezone, timedelta

import boto3
import requests

from common.logging_config import load_logging_config


def extract_neo_data_chunk(api_key: str, start_date: date, end_date: date, s3: boto3.client):
    """
    Extracts NASA Near-Earth Object (NEO) data and saves it to S3.
    :param api_key: The API key for NASA's NEO service
    :param start_date: The start date for the data extraction
    :param end_date: The end date for the data extraction
    :param s3: The S3 client for uploading data
    :return: None
    """

    if (end_date - start_date).days > 7:
        logger.critical('Chunk duration exceeds 7 days')
        return

    logger.info(f'Extracting NEO data from {start_date} to {end_date}')

    try:
        data_request = requests.get(
            'https://api.nasa.gov/neo/rest/v1/feed',
            params={
                'api_key': api_key,
                'start_date': start_date,
                'end_date': end_date,
            })
        data_request.raise_for_status()
        logger.info('Data request successful')
    except requests.exceptions.RequestException as e:
        logger.critical('Failed to retrieve data from NASA API', exc_info=e)
        return

    # Save full raw JSON
    full_data_key = f'neo/raw/from_{start_date}_to_{end_date}.json'
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

    for i, (key, entry) in enumerate(raw_json.get('near_earth_objects').items(), 1):
        # Save JSON entry partitioned by date
        date_str = key
        logger.info(f'Processing entry {i}/{len(raw_json)} for date {date_str}')

        entry_data_key = f'neo/date={date_str}/data/data.json'
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

    logger.info('NEO data extraction completed successfully')


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
    logger = logging.getLogger('neo_extractor')

    logger.info('Starting NEO data extraction')
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

    # Extract NEO data in chunks

    logger.info('Starting NEO data extraction in chunks')

    # Calculate the total duration
    input_start_date = args.start_date
    input_end_date = args.end_date
    total_duration = (input_end_date - input_start_date).days
    total_chunks = total_duration // 7 + (1 if total_duration % 7 > 0 else 0)
    current_chunk = 1

    # Track the current date
    chunk_start_date = input_start_date

    # Process data in chunks of 7 days or less

    while chunk_start_date < input_end_date:
        # Calculate the end date for this chunk
        logger.info(f'Processing chunk {current_chunk}/{total_chunks}')
        chunk_end_date = min(chunk_start_date + timedelta(days=6), input_end_date)

        # Extract data for this chunk
        extract_neo_data_chunk(nasa_api_key, chunk_start_date, chunk_end_date, s3_client)
        logger.info(f'Chunk {current_chunk} processed successfully')

        # Move to the next chunk
        chunk_start_date = chunk_end_date + timedelta(days=1)
        current_chunk += 1
