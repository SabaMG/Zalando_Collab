import json
import re
import base64
from urllib.parse import parse_qs

try:
    from src.functions.captcha import *
except ImportError:
    from functions.captcha import *
try:
    from spacescraper.datadome.magicnumber import *
except:
    from spacescraper.datadome.magicnumber import *

class Harvester(object):
    def __init__(self, session, user_agent, domain):

        self.session = session
        self.user_agent = user_agent

        self.domain = domain
    
    def set_headers(self, headers):
        self.user_agent = headers["user_agent"]
        self.sec_ch_ua = headers["sec-ch-ua"]
        self.platform = headers["sec-ch-ua-platform"]
    
    def prepare(self, response):
        if "var dd=" in response.text:
            challenge = response.text.split("var dd=")[1].split("</script>")[0]
            data = json.loads(challenge.replace("'", '"'))

            referer = response.url
            cid = self.session.cookies.get("datadome", None)
            if cid is None:
                raise Exception
            
            icid = data["cid"]
            hsh = data["hsh"]
            s = data["s"]
            t = data["t"]
            e = data["e"]
        
        else:
            challenge = json.loads(response.text)["url"]
            data = parse_qs(challenge.split("?")[1], keep_blank_values=True)

            icid = data["initialCid"][0]
            cid = data["cid"][0]
            referer = data["referer"][0]
            hsh = data["hash"][0]
            s = data["s"][0]
            t = data["t"][0]
            e = data["e"][0]
        
        self.parameters = {
            "initialCid": icid,
            "hash":	hsh,
            "t": t,
            "s": s,
            "referer": referer,
            "e": e,
            "cid": cid
        }

        return self.parameters
    
    def solve_first_challenge(self):
        headers = {
            "Host": "geo.captcha-delivery.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "iframe",
            "Referer": f"https://{self.domain}/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }

        parameters = {
            "initialCid": self.parameters["initialCid"],
            "hash":	self.parameters["hash"],
            "t": self.parameters["t"],
            "s": self.parameters["s"],
            "referer": self.parameters["referer"],
            "e": self.parameters["e"],
            "cid": self.parameters["cid"]
        }

        while True:
            response = self.session.get(
                f"https://geo.captcha-delivery.com/captcha/",
                headers=headers,
                params=parameters,
                timeout=60
            )

            if response:
                self.parent_url = response.url
                userEnv = re.findall(r'type="hidden" id="user_env" name="user_env" value="(.*?)">', response.text)[0]

                self.parameters.update({
                    "userEnv": userEnv
                })

                try:
                    self.sitekey = response.text.split("'sitekey' : ")[1].split(",")[0].replace("'", "")
                except Exception:
                    self.sitekey = None
                    self.gt = response.text.split("gt: '")[1].split("'")[0]
                    self.challenge = response.text.split("challenge: '")[1].split("'")[0]

                return True
    
    def solve_second_challenge(self): 
        headers = {
            "Host": "geo.captcha-delivery.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "sec-ch-ua-mobile": "?0",
            "User-Agent": self.user_agent,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": self.parent_url,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }

        if self.sitekey:
            while True:
                try:
                    captcha = solvecaptcha({
                        "type": "recaptcha",
                        "version": "2",
                        "sitekey": self.sitekey,
                        "url": self.parent_url,
                        "user-agent": self.user_agent
                    })

                    if captcha["Success"]:
                        token = captcha["Data"]
                        break

                except Exception:
                    continue

        else:
            while True:
                try:
                    captcha = solvecaptcha({
                        "type": "geetest",
                        "gt": self.gt,
                        "challenge": self.challenge,
                        "url": self.parent_url,
                    })

                    if captcha["Success"]:
                        break
                except Exception as e:
                    continue

        if self.sitekey:
            parameters = {
                "cid": self.parameters["cid"],
                "icid": self.parameters["initialCid"],
                "ccid": "",	
                "userEnv": self.parameters["userEnv"],
                "g-recaptcha-response": token,
                "hash":	self.parameters["hash"],
                "ua": self.user_agent,
                "referer": self.parameters["referer"],
                "parent_url": self.parent_url,
                "x-forwarded-for": "",	
                "captchaChallenge":	DatadomeMagicNumber(self.parameters["cid"], 10, self.user_agent).Generate(),
                "s": self.parameters["s"],
                "ir":""
            }
        else:
            parameters = {
                "cid": self.parameters["cid"],
                "icid": self.parameters["initialCid"],
                "ccid": "",	
                "userEnv": self.parameters["userEnv"],
                "geetest-response-challenge": captcha["Data"]["challenge"],
                "geetest-response-validate": captcha["Data"]["validate"],
                "geetest-response-seccode": captcha["Data"]["seccode"],
                "hash":	self.parameters["hash"],
                "ua": self.user_agent,
                "referer": self.parameters["referer"],
                "parent_url": self.parent_url,
                "x-forwarded-for": "",	
                "captchaChallenge":	DatadomeMagicNumber(self.parameters["cid"], 10, self.user_agent).Generate(),
                "s": self.parameters["s"],
                "ir":""
            }

        while True:
            response = self.session.get(
                f"https://geo.captcha-delivery.com/captcha/check",
                headers=headers,
                params=parameters,
                timeout=60
            )

            if response:
                self.cookie = response.json()["cookie"].split("datadome=")[1].split(";")[0]

                break
    
    def solve(self,response):
        self.session.logger.magenta("Solving DataDome Challenge")

        while True:
            self.prepare(response)

            if self.solve_first_challenge():

                self.solve_second_challenge()

                self.session.cookies.set("datadome", self.cookie, domain=self.domain.replace("www",""))

                return True
            
            else:
                self.session.logger.error("Error Solving DataDome Challenge")
                
                raise Exception

'''How to use the DataDome Harvester/Challenge Solver'''
'''
session = current session from Module
proxy = current proxy from Module
user_agent = User Agent used in the Module
domain = Domain of the Website

datadome = Harvester(session, proxy, user_agent, domain)

if datadome challenge presented the datadome.solve(response)

where "response" is the request response (not the response.text)
'''
