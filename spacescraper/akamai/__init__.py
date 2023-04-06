import json
try:
    from src.functions.constants import AKAMAI_API_KEY, AKAMAI_API_DOMAIN
except Exception:
    AKAMAI_API_KEY = ""
    AKAMAI_API_DOMAIN = ""
from .exceptions import SENSOR_NOT_FOUND_Exception
import base64
import re

class Akamai(object):
    def __init__(self, session, version, validation, validationInCookie, domain):
        self.version = version

        self.session = session
        self.delay = 1
        self.validCheck = validation
        self.validCheckInCookie = validationInCookie

        self.domain = domain

        self.cookie = f".{domain.split('.')[1]}.{domain.split('.')[2]}"
    
    def set_endpoint(self, endpoint):
        self.endpoint = endpoint
    
    def set_headers(self, headers):
        self.user_agent = headers["user_agent"]
        self.sec_ch_ua = headers["sec-ch-ua"]
        self.platform = headers["sec-ch-ua-platform"]

    def generate_sensor_data(self, dynamic, special_mode=None):
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": AKAMAI_API_KEY,
            "X-RapidAPI-Host": AKAMAI_API_DOMAIN,
            'accept-encoding': 'gzip, deflate, br'
        }       

        payload = {
            "url": f"https://{self.domain}",
            "abck": None,
            "bm_sz": None,
            "scriptUrl": self.endpoint,
            "type": 2,
            "userAgent": self.user_agent,
            "keyboard": False,
            #"dynamic": True,
            #"script": self.script
        }

        if special_mode:
            payload.update(
                {
                    "dynamic": dynamic,
                    "script": self.script
                }
            )

        while True:
            for c in self.session.cookies:
                if c.domain == self.cookie and c.name == "_abck":
                    payload["abck"] = c.value
                
                elif c.domain == self.cookie and c.name == "bm_sz":
                    payload["bm_sz"] = c.value
            
            response = self.session.post(
                "https://aka1.p.rapidapi.com/v2/web",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                try:
                    self.sensor_data = json.loads(response.text)["sensor"]

                    return self.sensor_data
                except:
                    print(response.text)
                    raise SENSOR_NOT_FOUND_Exception("no sensor data recived")

    def post_sensor_data(self, data):
        headers = {
            "host": self.domain,
            "connection": "keep-alive",
            "sec-ch-ua": self.sec_ch_ua,
            "content-type": "text/plain;charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "accept": "*/*",
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://{self.domain}",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        payload = {
            "sensor_data": data
        }

        while True:
            response = self.session.post(
                self.endpoint,
                headers=headers,
                data=json.dumps(payload, separators=(',', ':')),
                timeout=60
            )

            if response:
                for c in self.session.cookies:
                    if c.domain == self.cookie and c.name == "_abck":
                        _abck = c.value

                return _abck
    
    def get_first_sensor(self):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "origin": f"https://{self.domain}/",
            "referer": f"https://{self.domain}/",
            "user-agent": self.user_agent,
        }

        while True:
            response = self.session.get(
                self.endpoint,
                headers=headers,
                timeout=60
            )

            if response:
                self.script = base64.b64encode(response.text.encode('ascii')).decode('ascii')

                return True
    
    def solve(self, dynamic, special_mode=None):
        self.session.logger.magenta("Solving Bot Protection")

        self.get_first_sensor()

        while True:
            data = self.generate_sensor_data(dynamic=dynamic, special_mode=special_mode)

            if data:
                cookie = self.post_sensor_data(data)

                if self.validCheckInCookie:
                    if self.validCheck in cookie:
                        self.session.logger.magenta("Successfully Solved Protection")
                        return True
                    else:
                        continue
                else:
                    if self.validCheck in cookie:
                        continue
                    else:
                        self.session.logger.magenta("Successfully Solved Protection")
                    return True
    
    def get_pixel_script(self, script_url):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "origin": f"https://{self.domain}/",
            "referer": f"https://{self.domain}/",
            "user-agent": self.user_agent,
        }

        while True:
            response = self.session.get(
                script_url.replace("pixel_", ""),
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    str_idx = re.findall(r'g=_(\[(.+?)])', response.text)[0][1]
                    str_arr = re.findall(r'var\s*_=(.*?);', response.text)[0]
                    self.script_secret = eval(f'{str_arr}')[int(str_idx)]

                    return self.script_secret
                except:
                    raise Exception
            
    def get_pixel_payload(self, script_url, script_id, script_secret):
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": AKAMAI_API_KEY,
            "X-RapidAPI-Host": AKAMAI_API_DOMAIN,
            'accept-encoding': 'gzip, deflate, br'
        }

        payload = {
            "userAgent": self.user_agent,
            "script_id": script_id,
	        "script_secret": script_secret,
	        "url": script_url
        }

        while True:
            response = self.session.post(
                "https://aka1.p.rapidapi.com/pixel",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                return response.text
    
    def post_pixel_payload(self, data, script_url):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "origin": f"https://{self.domain}/",
            "referer": f"https://{self.domain}/",
            "user-agent": self.user_agent,
        }

        while True:
            response = self.session.post(
                script_url,
                headers=headers,
                data=data,
                timeout=60
            )

            if response:
                return True
    
    def solve_pixel(self, script_url, script_id):
        script_secret = self.get_pixel_script(script_url)

        if script_secret:
            payload = self.get_pixel_payload(script_url, script_id, script_secret)

            if payload:
                self.post_pixel_payload(payload, script_url)