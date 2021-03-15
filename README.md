# RSS SMS

**RSS SMS** is a script which allows you to subscribe to [RSS feeds](https://en.wikipedia.org/wiki/RSS) and be notified of certain posts by SMS if they match your desired keywords. For example, if you wanted to know about deals on [OzBargain](https://www.ozbargain.com.au) for CPUs, makeup or chocolates you could subscribe to their [RSS](https://www.ozbargain.com.au/deals/feed) feed and use the keywords *3900x*, *Mecca*, and *Ferrero Rocher* respectively. I find this script incredibly useful for this exact purpose as the deals I am interested in may run out of stock in as little as 60 minutes and checking OzBargain this frequently is impractical. Almost all news, podcast, and user forum sites have implemented RSS feeds for their content.

This readme will walk you through how to set up this script on your own hardware or using a variety of Amazon's services. If you have access to a free SMS API such as [Pushbullet](https://www.pushbullet.com/) or Telstra*, then you can run this script entirely for free.

*In the past, Telstra has offered 1,000 free SMS messages per month for its customers using their API, however I am unsure if this was the result of multiple promotions or just their normal policy.

# Table of Contents

- [Quick Start Guide](#quick-start-guide)
- [Set Up](#set-up)
- [Deployment](#deployment)
  - [Local](#local)
    - [Linux](#linux)
  - [AWS Lambda](#aws-lambda)
- [APIs](#apis)
  - [SMS](#sms)
  - [File Management](#file-management)
  - [URL Shortening](#url-shortening)
- [Limitations](#limitations)

# Quick Start Guide

To be written..

- Run locally
- Twilio SMS API

# Set Up

To get **RSS SMS** working you will need to [deploy it](#Deployment) and set up the chosen [APIs](#APIs). I strongly suggest that you set up and run **RSS SMS** locally to ensure that you can get it working before deploying it elsewhere. This will help to save you some sanity. 

The *config.yml* file is used to specify the RSS feeds and keywords that each mobile number is subscribed to. You can specify multiple mobile numbers, multiple RSS feeds for each number, and multiple keywords for each RSS feed. Most SMS APIs require you to use the [E.164](https://en.wikipedia.org/wiki/E.164) international telephone numbering plan. An example *config.yml* file is shown below.

```yaml
# Configuration file config.yml

# Australian Number
'+614XXXXXXXX':
  https://www.ozbargain.com.au/deals/feed:
    - 3900x
    - Mecca
    - Ferrero Rocher
  http://www.hellointernet.fm/podcast?format=rss:
  	- "#137"

# United States Number
'+14XXXXXXXX':
  ...
```

You will also need to set up a *.env* file or environment. The required variables will depend on the chosen APIs and will be described in [APIs](#apis).  

# Deployment

## Local

### Linux

You will have to clone the repo and install all of the dependencies. I recommend you use a virtual environment to install your dependencies as it will make deployment much easier if later use [AWS Lambda](#aws-lamda).

```bash
git clone <URL>
cd rss-sms
python3 -m venv .
source venv/bin/activate
pip3 install -r requirements.txt
```

I recommend you use the [local](#local-1) file management API to manage the *config.yml* and *texted.yml* files. This is configured at the top of the *main.py* file as shown below.

```python
# Import APIs
from file_apis.file_local import FileLocal

# Assign APIs
file_config = FileLocal()
file_texted = FileLocal()
```

You will also need to choose an SMS service as described [here](#sms). 

You will need to run **RSS SMS** constantly throughout the day so it can always check the most recent posts. You can accomplish this using [cron](https://man7.org/linux/man-pages/man8/cron.8.html) to create a cronjob that runs on a schedule. The following command will run *main.py* and log its output to *rss-sms.log* every 10 minutes. 

`*/10 * * * * PATH_TO/python3 PATH_TO/main.py >> ~/rss-sms.log`

## AWS Lambda

[AWS Lambda](https://aws.amazon.com/lambda/) provides you with a free and easy way to run **RSS SMS**. The online web console makes it easy to edit your *config.yml* file as needed. You have up to 1 million requests and 400,000 GB-seconds of computer time per month for free*. This is more than enough to run **RSS SMS** every 10 minutes or more.

To get started, you will need to create an IAM user as described [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console). Make sure you add the `AWS_ACCESS_KEY_ID` and ` AWS_SECRET_ACCESS_KEY` variables to your *.env* file or environment as these are required to use the AWS API as your user. Since AWS Lambda is stateless, you must use the [AWS S3 file management API](#aws-s3) or similar to manage the *texted.yml* file. The *config.yml* file however, may be managed using the [local file management API](#local-1). If you are using AWS Lambda and you do not have access to a free SMS API, I recommend that you use the AWS SNS service and double down on the Amazon ecosystem.

You will need to read the [APIs](#apis) section to set up each of the APIs. The top of the *main.py* file should look as follows.

```python
# Import APIs
from sms_apis.sms_aws import SmsAws
from file_apis.file_local import FileLocal
from file_apis.file_aws import FileAws

# Assign APIs
sms_client = SmsAws()
file_config = FileLocal()
file_texted = FileAws()
```

*As of 14/03/2021

### Lambda Function

You need to create a deployment zip file containing the required source files. Complete the following steps.

1. Create a new folder called *deployment*
2. Copy the *main.py* file into the deployment folder and rename it to *lambda_function.py*
3. Copy the *config.yml* file into the deployment folder
4. Copy the *file_apis*, *sms_apis* and *url_apis* folders into the deployment folder
5. Select and zip the **contents** of the deployment folder and name it *deployment.zip* 

You can now create the Lambda function. Complete the following steps.

1. Navigate to the [AWS Lambda console](https://console.aws.amazon.com/lambda/)
2. Select 'Functions' in the navigation pane
3. Click 'Create function'
4. Choose the following
   1. Author from scratch
   2. Name: rss-sms
   3. Runtime: Python3.X
5. Click 'Create function'
6. Click 'Upload from' and select '.zip file'
7. Upload the *deployment.zip* file that was created earlier

### Dependencies

AWS Lambda allows us to control our dependencies using Layers to reduce the size of our deployment file. Complete the following steps.

1. Create the following folders *python/lib/python3.X/site-packages/*
2. Copy the contents of the *site-packages* folder in your virtual environment and paste them into the folder created above
   1. Likely located at *venv/Lib/Python3.X/site-packages*, *venv/Lib/site-packages* or similar
3. Zip the root *python* folder and name it (i.e. *rss-sms-dependencies.zip*)
4. Navigate to the [AWS Lambda console](https://console.aws.amazon.com/lambda/)
5. Select 'Layers' in the navigation pane
6. Click 'Create layer'
7. Choose the following
   1. Name: rss-sms-dependencies
   2. Upload: Choose the *rss-sms-dependencies.zip* created earlier
   3. Compatible runtimes: Python3.X
8. Click 'Create'

You can now attach this dependency layer to our Lambda function. Complete the following steps.

1. Navigate to the [AWS Lambda console](https://console.aws.amazon.com/lambda/)
2. Select 'Functions' in the navigation pane
3. Click 'rss-sms' to edit it
4. Under 'Layers', click 'Add a layer'
5. Choose the following
   1. Custom layers
   2. Custom layers: rss-sms-dependencies
   3. Version: the latest version
6. Click 'Add'

### Misc Config

You need to change the function timeout limit as the default 3 seconds is not long enough. Complete the following steps.

1. Edit the 'rss-sms' Lambda function
2. In the 'Configuration' tab, select 'General configuration'
3. Click 'Edit'
4. Change the Timeout value to be 3 minutes and 0 seconds
5. Click 'Save'

You need to configure the environment variables used by **RSS SMS**. Complete the following steps.

1. Edit the 'rss-sms' Lambda function
2. In the 'Configuration' tab, select 'Environment variables'
3. Click 'Edit'
4. Click 'Add environment variable' and add the required environment variables
5. Click 'Save'

### Scheduling

You can now run **RSS SMS** by clicking 'Test', creating a test using the default values and running it. You should receive a text to your mobile if any of the RSS feeds contained any of the keywords from the *config.yml* file. However, you still need to schedule **RSS SMS** to run constantly. Complete the following steps.

1. Navigate to the [AWS CloudWatch console](https://console.aws.amazon.com/cloudwatch/)
2. Select 'Event' > 'Rules' in the navigation pane
3. Click 'Create rule'
4. Under 'Event Source', choose the following
   1. Schedule
   2. Fixed rate of: 10 minutes
5. Under 'Targets', click 'Add target' and choose the following
   1. Function: rss-sms
6. Click 'Configure details'
7. Choose the following
   1. Name: rss-sms-scheduler
8. Click 'Create rule'

**RSS SMS** should run immediately and then again every 10 minutes. Change the *config.yml* file to trigger on a recent post and run a test to verify that **RSS SMS** is sending texts correctly and on time.

### Updating config.yml

To change your subscriptions, you just need to edit the *config.yml* file and click 'Deploy' to save your changes. You can verify that your changes have worked by running a test.

# APIs

## SMS

### AWS Simple Notification Service (SNS)

You need to give the appropriate permissions to the AWS user you created earlier. Complete the following steps.

1. Navigate to the [AWS IAM console](https://console.aws.amazon.com/iam/home#/users)
2. Click on the user you created earlier to edit them
3. Add the following permissions to the user account
   1. `AmazonSNSFullAccess`

Add the following keys to your environment.

- `aws_region_name_sms`
  - You can find a list of SMS supported regions and their costs in this article [this article](https://docs.aws.amazon.com/sns/latest/dg/sns-supported-regions-countries.html).
- `monthly_spend_limit`
  - The maximum amount you want to spend each month on SMS. This may take up to an hour to update.
  - **Note**: By default, AWS limits your SMS quota to $1/month. If you wish to increase this limit, please follow the steps in [this article](https://docs.aws.amazon.com/sns/latest/dg/channels-sms-awssupport-spend-threshold.html). 

By default, the AWS SMS API uses the `Transactional` SMS type which ensures that the message is delivered over routes with the highest delivery reliability. This message type typically costs more than the `Promotional` SMS type, however in Australia these costs are the same*. 

*As of 14/03/2021

### Pushbullet

[Pushbullet](https://www.pushbullet.com/) is not currently supported although I'm planning to add support in the future as you can send up to 100* free SMS messages per month.

*As of 14/03/2021

### Twilio

[Twilio](https://www.twilio.com/) is not currently supported although I'm planning to add support in the future.

## File Management

### Local

Nothing needs to be configured for the local file management API.

### AWS S3

You need to give the appropriate permissions to the AWS user you created earlier. Complete the following steps.

1. Navigate to the [AWS S3 console](https://console.aws.amazon.com/s3/)
2. Click on the user you created earlier to edit them
3. Add the following permissions to the user account
   1. `AmazonS3FullAccess `

Add the following keys to your environment.

- `aws_region_name_file_management`
  - You can find a list of S3 supported regions and their costs in [this article](https://docs.aws.amazon.com/general/latest/gr/s3.html).
- `bucket_name`
  - The bucket used to store the already texted RSS posts is automatically created if it doesn't already exist.

## URL Shortening

### TinyURL

Nothing needs to be done to configure the [TinyURL](https://tinyurl.com/app) API, unless you require custom URLs which this API does not currently support. TinyURL was configured using their public URL shortening service is it produced some of the shortest URLs compared to other options and is free. 

# Limitations

Below are a list of known limitations for **RSS SMS**. 

- The only way to be notified of posts is via SMS. Receiving notifications via email for RSS feeds and keywords you care less about is a planned future feature.
- The way keywords are defined is not flexible and means you have to match the words from the post exactly. This can be a problem when trying to match multiple words or a phrase in a post.

# Contributions

If you would like to contribute a new API service, please create a merge request with a clear description of what the new API is, how to set it up, and how to use it. 