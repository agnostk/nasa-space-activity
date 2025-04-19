import sys
from datetime import datetime, timezone

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_date, trim


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
dyf = glueContext.create_dynamic_frame.from_catalog(
    database=GLUE_SOURCE_DATABASE,
    table_name=GLUE_SOURCE_TABLE,
    push_down_predicate=f'(date >= "{START_DATE}" and date <= "{END_DATE}")'
)
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
