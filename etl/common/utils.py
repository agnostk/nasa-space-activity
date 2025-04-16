import os

from dotenv import load_dotenv


def get_aws_resource(name: str):
    load_dotenv()

    return f'{os.getenv("AWS_RESOURCE_SUFFIX")}-{name}'
