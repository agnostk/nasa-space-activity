import sys
from datetime import datetime, timezone

import requests
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType


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


def fetch_threat_score(record):
    try:
        record = record.asDict()

        response = requests.post(
            f'{ENRICHMENT_API_URL}/neo-threat-score',
            headers={'x-api-key': ENRICHMENT_API_KEY},
            json={
                'diameter_min_km': record['diameter_min_km'],
                'diameter_max_km': record['diameter_max_km'],
                'velocity_kph': record['velocity_kph'],
                'miss_distance_km': record['miss_distance_km'],
                'hazardous': record['hazardous'],
            },
            timeout=10.0
        )
        response.raise_for_status()
        threat_score = response.json()['threat_score']
        record['threat_score'] = threat_score

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
enriched_rdd = source_df.rdd.map(fetch_threat_score)

# Define schema
schema = StructType([
    # Original fields from source schema
    StructField('asteroid_id', StringType(), True),
    StructField('asteroid_name', StringType(), True),
    StructField('absolute_magnitude_h', DoubleType(), True),
    StructField('diameter_min_km', DoubleType(), True),
    StructField('diameter_max_km', DoubleType(), True),
    StructField('hazardous', BooleanType(), True),
    StructField('close_approach_date', StringType(), True),
    StructField('velocity_kph', DoubleType(), True),
    StructField('miss_distance_km', DoubleType(), True),
    StructField('orbiting_body', StringType(), True),
    StructField('is_sentry_object', BooleanType(), True),
    StructField('sentry_data', StringType(), True),
    StructField('date', StringType(), True),

    # Enrichment fields
    StructField('threat_score', DoubleType(), True),
    StructField('enrichment_error', StringType(), True),
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
