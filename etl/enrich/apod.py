import sys
from datetime import datetime, timezone

import requests
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType


def get_glue_args(required_fields: [str], optional_args: dict):
    """
    Get command line arguments for Glue job.
    :param required_fields: list of mandatory fields for the job
    :param optional_args: dict of optional fields with default values
    :return: dict of arguments
    """

    given_optional_fields_key = list(set([i[2:] for i in sys.argv]).intersection([i for i in optional_args]))

    args = getResolvedOptions(sys.argv, required_fields + given_optional_fields_key)

    # Overwrite default value if optional args are provided
    optional_args.update(args)

    return optional_args


# Parse command line arguments
required_args = [
    'JOB_NAME',
    'glue_source_database',
    'glue_source_table',
    's3_target_path',
    'enrichment_api_url',
    'enrichment_api_key',
]

optional_args = {
    'start_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    'end_date': datetime.now(timezone.utc).strftime('%Y-%m-%d')
}
args = get_glue_args(required_args, optional_args)

GLUE_SOURCE_DATABASE = args['glue_source_database']
GLUE_SOURCE_TABLE = args['glue_source_table']
S3_TARGET_PATH = args['s3_target_path']
ENRICHMENT_API_URL = args['enrichment_api_url']
ENRICHMENT_API_KEY = args['enrichment_api_key']
START_DATE = args['start_date']
END_DATE = args['end_date']


def fetch_metadata(record):
    try:
        # Convert Row to dict to allow .get and mutation
        record = record.asDict()

        image_url = record.get('s3_path') or record.get('image_url')
        if not image_url:
            return record  # Skip if no image reference

        is_s3 = image_url.startswith('s3://')

        response = requests.post(
            f'{ENRICHMENT_API_URL}/image-metadata',
            headers={'x-api-key': ENRICHMENT_API_KEY},
            json={
                'image_url': image_url,
                'is_s3': is_s3
            },
            timeout=10.0
        )
        response.raise_for_status()
        metadata = response.json()

        # Add enrichment fields to record
        record.update({
            'average_color_r': metadata['average_color']['r'],
            'average_color_g': metadata['average_color']['g'],
            'average_color_b': metadata['average_color']['b'],
            'image_hash': metadata['image_hash'],
            'classification': metadata.get('classification', {}).get('top_class'),
            'classification_confidence': metadata.get('classification', {}).get('confidence'),
            'image_width': metadata.get('width'),
            'image_height': metadata.get('height'),
            'content_type': metadata.get('content_type'),
        })

    except Exception as e:
        record['enrichment_error'] = str(e)

    return record


# Initialize Glue context
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from Glue catalog based on provided date range
dyf = glueContext.create_dynamic_frame.from_catalog(
    database=GLUE_SOURCE_DATABASE,
    table_name=GLUE_SOURCE_TABLE,
    push_down_predicate=f'(date >= "{START_DATE}" and date <= "{END_DATE}")'
)
source_df = dyf.toDF()

# Convert DataFrame to RDD, apply enrichment, then back to DataFrame
enriched_rdd = source_df.rdd.map(fetch_metadata)

# Define schema
schema = StructType([
    # Original fields from source schema
    StructField('title', StringType(), True),
    StructField('copyright', StringType(), True),
    StructField('explanation', StringType(), True),
    StructField('media_type', StringType(), True),
    StructField('image_url', StringType(), True),
    StructField('s3_path', StringType(), True),
    StructField('date', StringType(), True),  # partition key

    # Enrichment fields
    StructField('average_color_r', IntegerType(), True),
    StructField('average_color_g', IntegerType(), True),
    StructField('average_color_b', IntegerType(), True),
    StructField('image_hash', StringType(), True),
    StructField('classification', StringType(), True),
    StructField('classification_confidence', DoubleType(), True),
    StructField('image_width', IntegerType(), True),
    StructField('image_height', IntegerType(), True),
])

# Infer schema back from enriched RDD (can also use a defined schema)
enriched_df = spark.createDataFrame(enriched_rdd, schema=schema)

# Write the enriched DataFrame to S3 in Parquet format
dyf_out = DynamicFrame.fromDF(enriched_df, glueContext, 'dyf_out')

glueContext.write_dynamic_frame.from_options(
    frame=dyf_out,
    connection_type='s3',
    connection_options={
        'path': S3_TARGET_PATH,
        'partitionKeys': ['date']
    },
    format='parquet'
)

job.commit()
