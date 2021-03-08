import yaml
import feedparser
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
import requests

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT").lower()
MAX_SMS_LENGTH = int(os.getenv("MAX_SMS_LENGTH"))

aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_region_name = os.getenv("aws_region_name")

if ENVIRONMENT == "aws":
    bucket_name = "s3-rss-sms"


def load_config():
    with open("config.yml") as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)

    if not config_data:
        raise Exception("Can't find config file.")

    return config_data


def load_texted_local():
    with open("texted.yml") as file:
        texted_data = yaml.load(file, Loader=yaml.FullLoader)

    if not texted_data:
        texted_data = {}

    return texted_data


def file_client_aws():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name
    )

    return s3_client


def load_texted_aws():
    # Create s3 client
    s3_client = file_client_aws()

    texted_data = {}

    # Check if bucket exists
    # TODO: There's probably a better way to check this
    bucket_exists = any(
        [b["Name"] == bucket_name for b in s3_client.list_buckets()["Buckets"]]
    )

    if not bucket_exists:
        try:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": aws_region_name,
                }
            )
        except ClientError as e:
            print("Error: Bucket didn't exist")
            print(e)

    # Get the texted file
    try:
        texted_file = s3_client.get_object(
            Bucket=bucket_name,
            Key="texted.yml",
        )
        file_data = texted_file["Body"].read().decode('ascii')
        texted_data = yaml.load(
            file_data,
            Loader=yaml.FullLoader
        )
    except ClientError as e:
        # File doesn't exist
        print("Error: Texted file doesn't exist")
        print(e)

    return texted_data


def stub_texted(config_data, texted_data):
    for mobile in config_data:
        if mobile not in texted_data:
            texted_data[mobile] = {
                'texts': 0
            }

        for rss_feed in config_data[mobile]:
            if rss_feed not in texted_data[mobile]:
                texted_data[mobile][rss_feed] = []


def text_posts(sms_client, posts_to_text, texted_data):
    for post in posts_to_text:
        try:
            text_result = sms_client.publish(
                PhoneNumber=post["mobile"],
                Message=post["message"],
                Subject="RSS SMS"
            )

            # Track the texted URLs
            texted_data[post["mobile"]]["texts"] += 1
            texted_data[post["mobile"]][post["rss_url"]].append(post["link"])

            print(f'Texted {post["mobile"]} deal {post["link"]}')
            print(text_result)
        except ClientError as e:
            print("Error: Failed to text deal")
            print(post)
            print(e)


def check_feeds(config_data, texted_data):
    posts_to_text = []

    for mobile in config_data:
        rss_urls = config_data[mobile]

        for rss_url in rss_urls:
            # Load the rss_feed
            rss_feed = feedparser.parse(rss_url)

            for post in rss_feed.entries:
                keywords = config_data[mobile][rss_url]

                for keyword in keywords:
                    stripped_post = {
                        "title": post["title"],
                        "summary": post["summary"],
                        "link": post["link"],
                        "mobile": mobile,
                        "rss_url": rss_url,
                        "keyword": keyword,
                    }

                    keyword = keyword.lower()

                    # Check if keyword is in the post, but not already texted
                    if (keyword in stripped_post["title"].lower() or
                        keyword in stripped_post["summary"].lower()) and \
                            stripped_post["link"] not in texted_data[mobile][rss_url]:
                        posts_to_text.append(stripped_post)
                        break

    return posts_to_text


def update_texted_local(texted_data):
    with open("texted.yml", "w") as file:
        yaml.dump(texted_data, file)


def update_texted_aws(texted_data):
    # Create s3 client
    s3_client = file_client_aws()

    data = yaml.dump(texted_data).encode('ascii')

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key="texted.yml",
            Body=data,
        )

        print("Updated texted file")
    except ClientError as e:
        print("Error: Failed to update texted file")
        print(e)


def sms_client_aws():
    # Create SNS client
    sns_client = boto3.client(
        "sns",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name
    )

    return sns_client


def clean_posts(posts_to_text):
    TINY_URL_PREFIX = "http://tinyurl.com/api-create.php?url="

    for post in posts_to_text:
        alert_text = f'Alert: {post["keyword"]}'
        post["short_link"] = requests.get(TINY_URL_PREFIX + post["link"])
        post["short_link"] = post["short_link"].text.split('//')[1]
        title_chars = MAX_SMS_LENGTH - len(alert_text) - len(post["short_link"]) - 2

        if title_chars != len(post["title"]):
            # Title section was shortened
            post["title"] = post["title"][:title_chars - 3] + "..."

        post["message"] = f'{alert_text}\n{post["title"]}\n{post["short_link"]}'

    return posts_to_text


if __name__ == "__main__":
    # Load config
    config = load_config()

    # Load texted
    if ENVIRONMENT == "local":
        texted = load_texted_local()
    elif ENVIRONMENT == "aws":
        texted = load_texted_aws()
    stub_texted(config, texted)

    # Check for posts to text
    posts = check_feeds(config, texted)

    # Prepare the posts for texting
    posts = clean_posts(posts)

    # Create sms client
    client = sms_client_aws()

    # Text the posts
    text_posts(client, posts, texted)

    # Update texted file
    if ENVIRONMENT == "local":
        update_texted_local(texted)
    elif ENVIRONMENT == "aws":
        update_texted_aws(texted)
