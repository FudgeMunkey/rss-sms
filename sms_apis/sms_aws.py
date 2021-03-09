from sms_apis.sms_api import SmsApi
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_region_name = os.getenv("aws_region_name")


class SmsAws(SmsApi):
    client = None

    def __init__(self):
        self.client = self.create_client()

    def send_sms(self, sms_data):
        try:
            self.client.publish(
                PhoneNumber=sms_data["mobile"],
                Message=sms_data["message"],
                Subject="RSS SMS"
            )

            print(f'Texted {sms_data["mobile"]} deal {sms_data["link"]}')
            result = True

        except ClientError as e:
            print(f"Error: Failed to send sms\n{e}")
            result = False

        return result

    def create_client(self):
        sms_client = boto3.client(
            "sns",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name
        )

        return sms_client
