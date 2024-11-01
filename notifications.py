import json
import urllib.request
import urllib.parse
import requests
from typing import List
import os
from logger import logger
from dotenv import load_dotenv
load_dotenv()

# SMS 
SMS_API = os.getenv("SMS_TOKEN")
SMS_URL = os.getenv("SMS_URL")
SMS_URL_BULK = os.getenv("SMS_URL_BULK")

def send_sms_bulk(phone_numbers: List,artist_name) -> bool:
    """
    Sends an SMS message to the specified numbers in a thread-safe manner.
    
    Args:
        phone_numbers (str): The recipient phone numbers.
        message (str): The message content.
    
    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    logger.info(f"Phone numbers Bulk {phone_numbers}")
    message = f"Get Ready To Win - Show Me The Money test - The artist is ({artist_name}) enter now. Text the word MONEY and the NAME OF THE ARTIST to 82122"

    
    messages = {
    'sender': "2WinAlerts",
    'messages': [
        {
            'number': number,
            'text': urllib.parse.quote(message)
        }
        for number in phone_numbers
    ]
                }
    
    logger.info(messages)

    # Prepare data for POST request
    data = {
        'apikey': SMS_API,
        'data': json.dumps(messages)
    }

    # Send the POST request
    response = requests.post('https://api.txtlocal.com/bulk_json/', data=data)

    # Print or return the response from Textlocal
    del messages
    return parse_sms_response(response.text)

def parse_sms_response(response_text):
    # Parse the JSON response
    response_data = json.loads(response_text)

    # Check if the status is 'success'
    if response_data.get('status') == 'success':
        # Extract message details
        messages_sent = len(response_data.get('messages', []))
        recipients = [msg['recipient'] for msg in response_data['messages'][0]['messages']]
        
        # Prepare the structured data
        data = {
            'messages_sent': messages_sent,
            'recipients': recipients,
            'status': response_data.get('status')
        }
        return [data, True]
    
    # If status is not 'success', return False
    return [None, False]