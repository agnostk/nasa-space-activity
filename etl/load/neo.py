import sys
from datetime import datetime, timezone

import boto3
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import to_date


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
    'db_user',
    'db_password_key',
    'rds_endpoint',
]

optional_args = {
    'start_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    'end_date': datetime.now(timezone.utc).strftime('%Y-%m-%d')
}
args = get_glue_args(required_args, optional_args)

GLUE_SOURCE_DATABASE = args['glue_source_database']
GLUE_SOURCE_TABLE = args['glue_source_table']
DB_USER = args['db_user']
DB_PASSWORD_KEY = args['db_password_key']
RDS_ENDPOINT = args['rds_endpoint']
START_DATE = args['start_date']
END_DATE = args['end_date']

# Initialize Glue context
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

secrets_manager_client = boto3.client('secretsmanager')
db_password = secrets_manager_client.get_secret_value(
    SecretId=DB_PASSWORD_KEY
)['SecretString']

# Read data from Glue catalog based on provided date range
dyf = glueContext.create_dynamic_frame.from_catalog(
    database=GLUE_SOURCE_DATABASE,
    table_name=GLUE_SOURCE_TABLE,
    push_down_predicate=f'(date >= "{START_DATE}" and date <= "{END_DATE}")'
)

source_df = dyf.toDF().withColumn('date', to_date('date', 'yyyy-MM-dd'))

dyf_out = DynamicFrame.fromDF(source_df, glueContext, 'dyf_out')

glueContext.write_dynamic_frame.from_options(
    frame=dyf_out,
    connection_type='postgresql',
    connection_options={
        'url': f'jdbc:postgresql://{RDS_ENDPOINT}/nasa',
        'user': DB_USER,
        'password': db_password,
        'dbtable': 'neo',
        'batchSize': '1000',
    }
)

job.commit()
