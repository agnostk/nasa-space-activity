import sys

import httpx
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

# Parse command line arguments using Glue's method
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'glue_source_database',
    'glue_source_table',
    's3_target_path',
    'enrichment_api_url',
    'enrichment_api_key',
])

GLUE_SOURCE_DATABASE = args['glue_source_database']
GLUE_SOURCE_TABLE = args['glue_source_table']
S3_TARGET_PATH = args['s3_target_path']
ENRICHMENT_API_URL = args['enrichment_api_url']
ENRICHMENT_API_KEY = args['enrichment_api_key']


def fetch_metadata(record):
    try:
        # Prioritize s3_path if available
        image_url = record.get("s3_path") or record.get("image_url")
        if not image_url:
            return record  # Skip if no image reference

        is_s3 = image_url.startswith("s3://")

        response = httpx.post(
            ENRICHMENT_API_URL,
            headers={"x-api-key": ENRICHMENT_API_KEY},
            json={
                "image_url": image_url,
                "is_s3": is_s3
            },
            timeout=10.0
        )
        response.raise_for_status()
        metadata = response.json()

        # Add enrichment fields to record
        record.update({
            "average_color_r": metadata["average_color"]["r"],
            "average_color_g": metadata["average_color"]["g"],
            "average_color_b": metadata["average_color"]["b"],
            "image_hash": metadata["image_hash"],
            "classification": metadata.get("classification", {}).get("top_class"),
            "classification_confidence": metadata.get("classification", {}).get("confidence"),
            "image_width": metadata.get("width"),
            "image_height": metadata.get("height"),
            "content_type": metadata.get("content_type"),
        })

    except Exception as e:
        record["enrichment_error"] = str(e)

    return record


# Initialize Glue context
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from Glue catalog
dyf = glueContext.create_dynamic_frame.from_catalog(database=GLUE_SOURCE_DATABASE, table_name=GLUE_SOURCE_TABLE)
source_df = dyf.toDF()

# Convert DataFrame to RDD, apply enrichment, then back to DataFrame
enriched_rdd = source_df.rdd.map(fetch_metadata)

# Infer schema back from enriched RDD (can also use a defined schema)
enriched_df = spark.createDataFrame(enriched_rdd)

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
