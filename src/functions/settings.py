import os
import platform
import sys
import json
import collections
import csv
import datetime
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from random import randint
import secrets
import string
#-------------------------------------------#

username = ""
version = ""

#-------------------------------------------#
def getPath() -> str:
    """
    returns the current path 
    """
    path = os.path.realpath(sys.argv[0])
    
    if platform.system() == 'Darwin':
        TestPath = str(path).replace('Test/Test', 'Test').replace('test_path.py', '').replace('quicktaskhandler.py', '').replace('/test.py', '').replace('test.app/Contents/MacOS/Test', 'Test.app/Contents/Resources').replace('settings.py', '').replace("src","").replace("functions","").replace("main.py","").replace("create_profile.py","")
    else:
        TestPath = str(path).replace('app.py', '').replace('quicktaskhandler.py', '').replace('Test.exe', '').replace('test.py', '').replace('settings.py', '').replace("src","").replace("functions","").replace("main.py","").replace("create_profile.py","").replace("webhook.py","").replace("test.py","")
    
    return str(TestPath).replace('test.exe', '').replace('taskmanager.py', '').replace('notifications.py', '').replace('captcha_harvester.py',"").replace("create_backup.py","")

def getSettingsdata():
    try:
        path = getPath() + "/settings.json"
        with open(path) as f:
            return {"success":True,"data":json.load(f)}
    except Exception as e:
        return {"success":False,"reason":e}

def getSettings() -> str:
    return getPath() + "/settings.json"

def getKey() -> str:
    """
    returns license key from settings.json
    """
    settings = getSettings()
    with open(settings) as f:
        data = json.load(f)
    return data['License key']

def getWebhook() -> str:
    """
    returns webhook from settings.json
    """
    settings = getSettings()
    with open(settings) as f:
        data = json.load(f)
    return data['Webhook']

def getRetryDelay() -> float:
    """
    returns Retry Delay from settings.json
    """
    try:
        settings = getSettings()
        with open(settings) as f:
            data = json.load(f)
        return float(data['Retry Delay'])
    except Exception as e:
        return {"success":False,"reason":e}

def getMonitorDelay() -> float:
    """
    returns Monitor Delay from settings.json
    """
    try:
        settings = getSettings()
        with open(settings) as f:
            data = json.load(f)
        return float(data['Monitor Delay'])
    except Exception as e:
        return {"success":False,"reason":e}



def clearTerminal():
    try:
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
    except Exception as e:
        pass



def save_profile(profile_data):
    try:
        with open(getPath()+"/profiles.csv",newline='') as f:
            r = csv.reader(f)
            data = [line for line in r]
            try:
                del data[0]
            except:
                pass
            
        data.append(profile_data)
        with open(getPath()+"/profiles.csv",'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['PROFILE_NAME', 'FIRSTNAME', 'LASTNAME', 'STREET_1', 'STREET_2', 'HOUSENUMBER', 'CITY', 'ZIPCODE', 'PROVINCE', 'COUNTRY', 'PHONENUMBER', 'EMAIL', 'CREDITCARD_HOLDER', 'CREDITCARD_NUMBER', 'CREDITCARD_MONTH', 'CREDITCARD_YEAR', 'CREDITCARD_CVV','WEBHOOK'])
            w.writerows(data)
        return {"success":True}
    except Exception as e:
        return {"success":False,"reason":e}
    
def save_checkout(checkout_data):
    try:
        with open(getPath()+"/config/success.csv",newline='') as f:
            r = csv.reader(f)
            data = [line for line in r]
            try:
                del data[0]
            except:
                pass
            
        data.append([datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")]+checkout_data)
        with open(getPath()+"/config/success.csv",'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(["TIME","STORE","PRODUCT","URL / PID","SIZE","EMAIL","PAYMENT METHOD","CHECKOUT LINK"])
            w.writerows(data)
        return {"success":True}
    except Exception as e:
        return {"success":False,"reason":e}



def get_csv(path=getPath()+"/profiles.csv"):
    try:
        data = []
        with open(path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)    
            return {"success":True,"data":json.loads(json.dumps(data))}
    except Exception as e:
        return {"success":False,"reason":e}

def delete_profile(name:str):
    try:
        new_profiles = []
        with open(getPath()+"/profiles.csv",newline='') as f:
            r = csv.reader(f)
            data = [line for line in r]
            try:
                del data[0]
            except:
                pass
            
        for i in data:
            if i != [] and i[0] != name:
                new_profiles.append(i)
        with open(getPath()+"/profiles.csv",'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['PROFILE_NAME', 'FIRSTNAME', 'LASTNAME', 'STREET_1', 'STREET_2', 'HOUSENUMBER', 'CITY', 'ZIPCODE', 'PROVINCE', 'COUNTRY', 'PHONENUMBER', 'EMAIL', 'CREDITCARD_HOLDER', 'CREDITCARD_NUMBER', 'CREDITCARD_MONTH', 'CREDITCARD_YEAR', 'CREDITCARD_CVV','WEBHOOK'])
            w.writerows(new_profiles)
        return {"success":True}
    except Exception as e:
        return {"success":False,"reason":e}

def write_settings(settings):
    try:
        with open(getPath() + "/settings.json", 'w') as json_file:
            json.dump(settings, json_file,indent=4)
        return {"success":True}
    except Exception as e:
        return {"success":False,"reason":e}

def delete_n_line(n=1):
    "Use this function to delete the last line in the STDOUT"

    #cursor up one line
    for i in range(n):
        sys.stdout.write('\x1b[1A')

        #delete last line
        sys.stdout.write('\x1b[2K')

def resource_path(file):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, file)
    
    return getPath() + f"/{file}"#os.path.join(os.path.abspath("."), file)#

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def generatePassword(len=20):
    return ''.join(secrets.choice(string.ascii_letters + string.digits + '~:+[@^{%(-*&<}._=]>;?#$)/') for i in range(len))


def save_account(account_data):
    try:
        with open(getPath()+"/config/account.csv",newline='') as f:
            r = csv.reader(f)
            data = [line for line in r]
            try:
                del data[0]
            except:
                pass
        data.append(account_data)
        with open(getPath()+"/config/account.csv",'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(["STORE","EMAIL","PASSWORD"])
            w.writerows(data)
        return {"success":True}
    except Exception as e:
        return {"success":False,"reason":e}