from file_apis.file_api import FileApi
import os
import yaml
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
AWS_REGION_NAME = os.getenv("aws_region_name_file_management")
BUCKET_NAME = os.getenv("bucket_name")

if not AWS_ACCESS_KEY_ID:
    raise Exception("Missing aws_access_key_id from the environment.")

if not AWS_SECRET_ACCESS_KEY:
    raise Exception("Missing aws_secret_access_key from the environment.")

if not AWS_REGION_NAME:
    raise Exception("Missing aws_region_name from the environment.")

if not BUCKET_NAME:
    raise Exception("Missing bucket_name from the environment.")


class FileAws(FileApi):
    client = None

    def __init__(self):
        self.client = self.create_client()

    def read_file_yaml(self, file_path):
        try:
            file_object = self.client.get_object(
                Bucket=BUCKET_NAME,
                Key="texted.yml",
            )
            file_data = file_object["Body"].read().decode('ascii')

            file_data = yaml.load(
                file_data,
                Loader=yaml.FullLoader
            )
        except ClientError as e:
            # File doesn't exist
            print(f"Error: Unable to load file\n{e}")

        return file_data if file_data else {}

    def write_file_yaml(self, file_path, data):
        # TODO: Error handling
        binary_data = yaml.dump(data).encode('ascii')

        try:
            self.client.put_object(
                Bucket=BUCKET_NAME,
                Key="texted.yml",
                Body=binary_data,
            )

            print("Updated texted file")
        except ClientError as e:
            print(f"Error: Failed to update texted file\n{e}")

    def create_client(self):
        aws_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION_NAME
        )

        # Create the bucket if it doesn't exist
        # TODO: There's probably a better way to check this
        bucket_exists = any(
            [b["Name"] == BUCKET_NAME for b in aws_client.list_buckets()["Buckets"]]
        )

        if not bucket_exists:
            try:
                aws_client.create_bucket(
                    Bucket=BUCKET_NAME,
                    CreateBucketConfiguration={
                        "LocationConstraint": AWS_REGION_NAME,
                    }
                )
            except ClientError as e:
                print(f"Error: Couldn't create bucket\n{e}")

        return aws_client
