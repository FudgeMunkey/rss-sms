from file_apis.file_api import FileApi
import os
import yaml
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_region_name = os.getenv("aws_region_name")


class FileAws(FileApi):
    client = None
    bucket_name = "s3-rss-sms"

    def __init__(self):
        self.client = self.create_client()

    def read_file_yaml(self, file_path):
        try:
            file_object = self.client.get_object(
                Bucket=self.bucket_name,
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
                Bucket=self.bucket_name,
                Key="texted.yml",
                Body=binary_data,
            )

            print("Updated texted file")
        except ClientError as e:
            print(f"Error: Failed to update texted file\n{e}")

    def create_client(self):
        aws_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name
        )

        # Create the bucket if it doesn't exist
        # TODO: There's probably a better way to check this
        bucket_exists = any(
            [b["Name"] == self.bucket_name for b in aws_client.list_buckets()["Buckets"]]
        )

        if not bucket_exists:
            try:
                aws_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": aws_region_name,
                    }
                )
            except ClientError as e:
                print(f"Error: Couldn't create bucket\n{e}")

        return aws_client
