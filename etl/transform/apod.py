import sys

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, asc, to_date, trim

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
dyf = glueContext.create_dynamic_frame.from_catalog(database=GLUE_SOURCE_DATABASE, table_name=GLUE_SOURCE_TABLE)
source_df = dyf.toDF()

# Join image paths from S3
df_data = (source_df.filter(col('partition_1') == 'data')
           .select('date', 'title', 'copyright', 'explanation', 'media_type', 'url'))
df_meta = (source_df.filter(col('partition_1') == 'meta')
           .select('date', 's3_path'))

join_df = df_data.join(df_meta, on='date', how='left')

# Clean the DataFrame
clean_df = join_df.dropDuplicates(['date'])
clean_df = join_df.withColumn('date', to_date('date', 'yyyy-MM-dd'))
print(f'Cleaned {join_df.count() - clean_df.count()} rows.')

# Remove leading and trailing spaces from string columns
for col_name in ['title', 'explanation', 'copyright']:
    if col_name in clean_df.columns:
        clean_df = clean_df.withColumn(col_name, trim(col(col_name)))

# Fill missing values with default values
clean_df = clean_df.fillna({
    'title': 'Unknown',
    'explanation': 'Unknown',
    'copyright': 'Unknown',
    'media_type': 'Unknown',
})

# Write the cleaned DataFrame to S3 in Parquet format
dyf_out = DynamicFrame.fromDF(clean_df, glueContext, 'dyf_out')

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
