import json
import mimetypes
from argparse import ArgumentParser
from datetime import date, datetime, timezone
from urllib.parse import urlparse

import boto3
import requests


def extract_apod_data(api_key: str, start_date: date, end_date: date, s3: boto3.client):
    data_request = requests.get(
        'https://api.nasa.gov/planetary/apod',
        params={
            'api_key': api_key,
            'start_date': start_date,
            'end_date': end_date,
            'thumbs': True,
        })

    data_request.raise_for_status()

    # Save full raw JSON
    full_data_key = f'apod/raw/from_{start_date}_to_{end_date}.json'
    full_data_bytes = data_request.content

    s3.put_object(
        Bucket='nasa-bronze',
        Key=full_data_key,
        Body=full_data_bytes,
        ContentType='application/json'
    )

    raw_json = data_request.json()

    for entry in raw_json:
        # Save JSON entry partitioned by date
        date_str = entry.get('date')
        entry_data_key = f'apod/date={date_str}/data.json'
        entry_data_bytes = json.dumps(entry).encode('utf-8')
        s3.put_object(
            Bucket='nasa-bronze',
            Key=entry_data_key,
            Body=entry_data_bytes,
            ContentType='application/json'
        )

        media_type = entry.get('media_type')
        image_url = entry.get('url') \
            if media_type == 'image' \
            else entry.get('thumbnail_url')

        image_path = urlparse(image_url).path
        image_extension = image_path.split('.')[-1]
        image_content_type = mimetypes.types_map.get(f'.{image_extension}', 'application/octet-stream')

        image_request = requests.get(image_url)
        image_request.raise_for_status()

        # Save image to S3 partitioned by date
        image_key = f'apod/date={date_str}/image.{image_extension}'
        image_bytes = image_request.content
        s3.put_object(
            Bucket='nasa-bronze',
            Key=image_key,
            Body=image_bytes,
            ContentType=image_content_type
        )


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
                        help='Run locally while connecting to AWS (requires AWS CLI SSO profile)')
    args = parser.parse_args()

    # Initialize AWS session
    if args.local:
        # When running locally, use the AWS CLI SSO profile
        boto3.setup_default_session(profile_name=args.profile)

    # Initialize AWS Secrets Manager client
    secrets_manager_client = boto3.client('secretsmanager', region_name=args.region)

    # Get API key from AWS Secrets Manager
    try:
        nasa_api_key = secrets_manager_client.get_secret_value(SecretId='nasa_API_key')['SecretString']
    except Exception as e:
        print(f'Error retrieving API key: {e}')
        exit(1)

    # Initialize S3 client
    s3_client = boto3.client('s3', region_name=args.region)

    # Extract APOD data
    extract_apod_data(nasa_api_key, args.start_date, args.end_date, s3_client)
