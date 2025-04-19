import sys
from datetime import datetime, timezone

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_date, explode


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
    's3_target_path'
]

optional_args = {
    'start_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    'end_date': datetime.now(timezone.utc).strftime('%Y-%m-%d')
}
args = get_glue_args(required_args, optional_args)

GLUE_SOURCE_DATABASE = args['glue_source_database']
GLUE_SOURCE_TABLE = args['glue_source_table']
S3_TARGET_PATH = args['s3_target_path']
START_DATE = args['start_date']
END_DATE = args['end_date']

# Initialize Glue context
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from Glue catalog
dyf = glueContext.create_dynamic_frame.from_catalog(database=GLUE_SOURCE_DATABASE, table_name=GLUE_SOURCE_TABLE)
source_df = dyf.toDF()

# Filter only 'data' partition
df_data = source_df.filter(col('partition_1') == 'data')

# Explode close_approach_data
exploded_df = df_data.withColumn("approach", explode(col("close_approach_data")))
exploded_df.select("id", "approach.close_approach_date").show(3, truncate=False)

# Flatten the dataframe
flattened_df = exploded_df.select(
    col("date"),
    col("id").alias("asteroid_id"),
    col("name").alias("asteroid_name"),
    col("absolute_magnitude_h"),
    col("estimated_diameter.kilometers.estimated_diameter_min").alias("diameter_min_km"),
    col("estimated_diameter.kilometers.estimated_diameter_max").alias("diameter_max_km"),
    col("is_potentially_hazardous_asteroid").alias("hazardous"),
    col("approach.close_approach_date"),
    col("approach.relative_velocity.kilometers_per_hour").cast("double").alias("velocity_kph"),
    col("approach.miss_distance.kilometers").cast("double").alias("miss_distance_km"),
    col("approach.orbiting_body"),
    col("is_sentry_object"),
    col("sentry_data")
)

# Normalize and cleanse
flattened_df = flattened_df.withColumn("date", to_date(col("date"), "yyyy-MM-dd"))
flattened_df = flattened_df.fillna({
    "asteroid_name": "Unknown",
    "velocity_kph": 0.0,
    "miss_distance_km": 0.0,
    "orbiting_body": "Unknown"
})

# Fill missing values with default values
final_df = flattened_df.fillna({
    'asteroid_id': 'Unknown',
    'asteroid_name': 'Unknown',
    'sentry_data': 'Unknown',
})

# Write the cleaned DataFrame to S3 in Parquet format
dyf_out = DynamicFrame.fromDF(final_df, glueContext, 'dyf_out')

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
