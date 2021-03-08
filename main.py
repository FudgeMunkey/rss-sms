import yaml
import feedparser
import boto3
from dotenv import load_dotenv
import os


def load_config():
    with open("config.yml") as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)

    if not config_data:
        raise Exception("Can't find config file.")

    return config_data


def load_texted():
    with open("texted.yml") as file:
        texted_data = yaml.load(file, Loader=yaml.FullLoader)

    if not texted_data:
        texted_data = {}

    return texted_data


def stub_texted(config_data, texted_data):
    # TODO: Also stub new rss urls
    for mobile in config_data:
        if mobile not in texted_data:
            texted_data[mobile] = {
                'texts': 0
            }

            for rss_feed in config_data[mobile]:
                texted_data[mobile][rss_feed] = []


def text_posts(sms_client, posts_to_text, texted_data):
    # TODO: Handle texting errors

    for post in posts_to_text:
        text_result = sms_client.publish(
            PhoneNumber=post["mobile"],
            Message=post["message"],
            Subject="RSS SMS"
        )

        # Track the texted URLs
        texted_data[post["mobile"]]["texts"] += 1
        texted_data[post["mobile"]][post["rss_url"]].append(post["link"])


def check_feeds(config_data, texted_data):
    posts_to_text = []

    for mobile in config_data:
        print(f"Scanning for {mobile}")
        rss_urls = config_data[mobile]

        for rss_url in rss_urls:
            # Load the rss_feed
            print(f"loading rss feed {rss_url}")

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


def update_texted(texted_data):
    with open("texted.yml", "w") as file:
        yaml.dump(texted_data, file)


def aws_client():
    load_dotenv()

    aws_access_key_id = os.getenv("aws_access_key_id")
    aws_secret_access_key = os.getenv("aws_secret_access_key")
    aws_region_name = os.getenv("aws_region_name")

    # Create SNS client
    sns_client = boto3.client(
        "sns",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name
    )

    return sns_client


def clean_posts(posts_to_text):
    # TODO: Clean up/optimise the posts

    for post in posts_to_text:
        sms_message = f'Alert {post["keyword"]}\n{post["title"]}\n{post["link"]}'

        if len(sms_message) > 160:
            # TODO: Optimisations around character length
            print(f"Too many characters..\n{sms_message}")
            sms_message = f'Alert {post["keyword"]}\n{post["link"]}'

        post["message"] = sms_message

    return posts_to_text


if __name__ == "__main__":
    # Load config
    config = load_config()

    # Load texted
    texted = load_texted()
    stub_texted(config, texted)

    # Check for posts to text
    posts = check_feeds(config, texted)

    # Prepare the posts for texting
    posts = clean_posts(posts)

    # Create sms client
    client = aws_client()

    # Text the posts
    text_posts(client, posts, texted)

    # Update texted file
    update_texted(texted)
