import boto3
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

AWS_REGION = 'us-east-1'
USERS_TABLE = 'travelgo_user'
SERVICE_TABLE = 'travelgo_service'
BOOKING_TABLE = 'travelgo_booking'
PAYMENT_TABLE = 'travelgo_payment'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:xxxx:stocker_alerts'
SES_SENDER_EMAIL = 'verified-sender@example.com'

# AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)
ses_client = boto3.client('ses', region_name=AWS_REGION)

# Tables
users_table = dynamodb.Table(USERS_TABLE)
service_table = dynamodb.Table(SERVICE_TABLE)
booking_table = dynamodb.Table(BOOKING_TABLE)
payment_table = dynamodb.Table(PAYMENT_TABLE)

def send_sns_notification(message):
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="New TravelGo Booking"
    )

def send_email(recipient, subject, body):
    ses_client.send_email(
        Source=SES_SENDER_EMAIL,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
