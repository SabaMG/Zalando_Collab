import requests
import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import timezone
import datetime
import json
from threading import Thread
import traceback

def generateHeader(module=False):
    """
    generates encrpyted header for our API`s

    :param modules:str -> if request being made to our module api
    """
    pass

# ------------------------------------------------------------------------------- #

def generateDATA(data : json) -> str:
    """
    generates encrpyted data from json

    :param data:json -> data to encrypt

    :return: str -> encrypted data
    """
    pass

# ------------------------------------------------------------------------------- #

def encrypt_decrypt(data: bytes) -> bytes:
    """Encrypt / Decrypt data using the static key
        
    Args:
        data (bytes): Data to encrypt /decrypt
        
    Returns:
        bytes: Encrypted / Decrypted data
    """
    pass

# ------------------------------------------------------------------------------- #

def generateUrl(scraper,url:str,domain_name=None):
    """
    generates a url for the webhook

    :param scraper: requests.Session -> scraper session
    :param url:str -> url to include in the webhook
    :param domain_name:str -> domain name of the site

    :return: str -> url for the webhook
    """
    pass

# ------------------------------------------------------------------------------- #

def generateID(discordID):
    """
    generates a unique ID for the users quicktasks

    :param discordID: -> discord ID of the user

    :return: str -> unique ID
    """
    pass

# ------------------------------------------------------------------------------- #

def storeCheckout(data: dict):
    """
    stores the checkout data of a user in our database
    
    :param data: dict -> data to store
    """
    pass
