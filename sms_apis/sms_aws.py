from sms_apis.sms_api import SmsApi
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
AWS_REGION_NAME = os.getenv("aws_region_name_sms")
MONTHLY_SPEND_LIMIT = os.getenv("monthly_spend_limit")

if not AWS_ACCESS_KEY_ID:
    raise Exception("Missing aws_access_key_id from the environment.")

if not AWS_SECRET_ACCESS_KEY:
    raise Exception("Missing aws_secret_access_key from the environment.")

if not AWS_REGION_NAME:
    raise Exception("Missing aws_region_name from the environment.")

if not MONTHLY_SPEND_LIMIT:
    raise Exception("Missing monthly_spend_limit from the environment.")


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
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION_NAME
        )

        sms_client.set_sms_attributes(
            attributes={
                "MonthlySpendLimit": MONTHLY_SPEND_LIMIT,
                "DefaultSenderID": "RSSSMS",
                "DefaultSMSType": "Transactional"
            }
        )

        return sms_client
