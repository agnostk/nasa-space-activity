import sys

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, trim, explode

# Parse command line arguments using Glue's method
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'glue_source_database',
    'glue_source_table',
    's3_target_path'
])

GLUE_SOURCE_DATABASE = args['glue_source_database']
GLUE_SOURCE_TABLE = args['glue_source_table']
S3_TARGET_PATH = args['s3_target_path']

# Initialize Glue context
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from Glue catalog
dyf = glueContext.create_dynamic_frame.from_catalog(database=GLUE_SOURCE_DATABASE, table_name=GLUE_SOURCE_TABLE)
source_df = dyf.toDF()

# Join image paths from S3
df_data = source_df.filter(col('partition_1') == 'data')
df_meta = source_df.filter(col('partition_1') == 'meta').select('id', 's3_path', 'content_type', 'image_url')

# Explode the photos column
df_exploded = df_data.select('id', 'date', explode('photos').alias('photo'))

# Normalize the exploded DataFrame
df_normalized = df_exploded.select(
    col('id').alias('record_id'),
    col('date'),
    col('photo.id').alias('photo_id'),
    col('photo.sol'),
    col('photo.camera.id').alias('camera_id'),
    col('photo.camera.name').alias('camera_name'),
    col('photo.camera.full_name').alias('camera_full_name'),
    col('photo.img_src'),
    col('photo.earth_date'),
    col('photo.rover.name').alias('rover_name'),
    col('photo.rover.status').alias('rover_status'),
)

# Join with metadata
final_df = df_normalized.join(df_meta, df_normalized.photo_id == df_meta.id, how='left') \
    .select(
    'date', 'photo_id', 'sol',
    'camera_id', 'camera_name', 'camera_full_name',
    'img_src', 'earth_date', 'rover_name',
    's3_path', 'content_type', 'image_url'
)

# Remove leading and trailing spaces from string columns
for col_name in ['camera_name', 'camera_full_name', 'rover_name']:
    if col_name in final_df.columns:
        final_df = final_df.withColumn(col_name, trim(col(col_name)))

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
