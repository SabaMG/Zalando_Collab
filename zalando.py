try: 
    from spacescraper import *
except ImportError: 
    from spacescraper import *

try: 
    from spacescraper.akamai import *
except ImportError: 
    from spacescraper.akamai import *

try:
    from src.functions.settings import *
except ImportError: 
    from functions.settings import *
try:
    from src.functions.api import *
except ImportError: 
    from functions.api import *
try:
    from src.functions.programtitle import *
except ImportError: 
    from functions.programtitle import *
# try:
#     from src.functions.webhook import *
# except ImportError: 
#     from src.functions.webhook import *

import src.functions.constants as constants
import json
import requests
import time
import random
import urllib
import uuid
import re

DEV_MODE = False
class ZALANDO(object):
    def __init__(self, task):
        self.task = task
        self.titelbar = MODULETITEL({"store":"Zalando","values": ["Task(s)","Carts","Failed","Success"]}).status_bar
        self.titelbar("Task(s)")
        self.session = SpaceScraper.create_session(
            module_name = "ZALANDO",
            taskcount = self.task["tasknumber"],
            proxyList = self.task["proxy"],
            requestPostHook = self.injection,
            tls = True
        )

        if DEV_MODE:
            self.session.proxies =  {"http": "http://127.0.0.1:8888", "https": "http://127.0.0.1:8888"}

        if self.task["DOMAIN"] == "DE":
            self.domain = "www.zalando.de"
        elif self.task["DOMAIN"] == "AT":
            self.domain = "www.zalando.at"
        elif self.task["DOMAIN"] == "CZ":
            self.domain = "www.zalando.cz"
        elif self.task["DOMAIN"] == "NL":
            self.domain = "www.zalando.nl"
        elif self.task["DOMAIN"] == "ES":
            self.domain = "www.zalando.es"
        elif self.task["DOMAIN"] == "FR":
            self.domain = "www.zalando.fr"
        elif self.task["DOMAIN"] == "UK":
            self.domain = "www.zalando.co.uk"
        elif self.task["DOMAIN"] == "RO":
            self.domain = "www.zalando.ro"
        elif self.task["DOMAIN"] == "PL":
            self.domain = "www.zalando.pl"
        elif self.task["DOMAIN"] == "BE":
            self.domain = "www.zalando.be"
        elif self.task["DOMAIN"] == "HR":
            self.domain = "www.zalando.hr"
        elif self.task["DOMAIN"] == "DK":
            self.domain = "www.zalando.dk"
        elif self.task["DOMAIN"] == "HU":
            self.domain = "www.zalando.hu"
        elif self.task["DOMAIN"] == "IT":
            self.domain = "www.zalando.it"
        elif self.task["DOMAIN"] == "SK":
            self.domain = "www.zalando.sk"
        elif self.task["DOMAIN"] == "CH":
            self.domain = "www.zalando.ch"
        else:
            raise Exception("Country not supported")
        
        self.confirgutate(self.session)

        self.instance = Akamai(self.session, "v2", "||", False, self.domain)
        self.solver = Akamai(self.session, "v2", "||", False, "accounts.zalando.com")

        self.instance.set_headers({
            "user_agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-platform": self.platform
        })

        self.solver.set_headers({
            "user_agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-platform": self.platform
        })

        self.utils()
        self.prepare()
        self.login()
        self.initialise()
        self.preload()
        self.handle_checkout()
        self.monitor()
        self.cart()

        if bool(self.items):
            for item in self.items:
                self.clear_cart(item)
        
        if self.task["EXCLUSIVE"].strip().lower() in ["true", "yes"]:
            self.exclusive()
        else:
            self.carting()

        self.scrape_checkout_data()
        self.order()
        
        sys.exit()

    def confirgutate(self, session):
        self.user_agent = random.choice(constants.user_agents)

        self.version = session.get_chrome_version(self.user_agent)
        self.platform = session.get_ua_platform(self.user_agent)
        self.sec_ch_ua = session.get_chrome_sec_ch_ua(self.version)

        session.bifrost.h2_frame_settings = {
            'HEADER_TABLE_SIZE': 65536,
            'MAX_CONCURRENT_STREAMS': 1000,
            'INITIAL_WINDOW_SIZE': 6291456,
            'MAX_HEADER_LIST_SIZE': 262144,
        }

    def utils(self):

        self.task["SIZE"] = self.task["SIZE"].split(";")

    def prepare(self):
        self.session.logger.warn("Initializing Session [1]")

        headers = {
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/myaccount/",
                headers=headers,
                timeout=60,
                allow_redirects=True
            )

            if response:
                try:
                    endpoint = response.text.split('type="text/javascript"  src="')[1].split('">')[0]

                    self.solver.set_endpoint(
                        f"https://accounts.zalando.com{endpoint}"
                    )

                    self.pixel_id = response.text.split('bazadebezolkohpepadr="')[1].split('"')[0]
                    self.pixel_url = response.text.split('img src="')[1].split('?')[0]

                    self.login_url = response.url
                    self.request = self.login_url.split("request=")[1].split("&")[0]
                    self.csrf_token = self.session.cookies["csrf-token"]

                    parsed = self.session.prettify(response.text)

                    self.flow_id = json.loads(urllib.parse.unquote(parsed.find("div", {"id": "sso"})["data-render-headers"]))["x-flow-id"]

                    self.session.logger.success("Succesfully Initialized Session [1]")
                    break
                except:
                    self.session.logger.error("Error Initializing Session [1]")
                    time.sleep(getRetryDelay())
                    continue

    def login(self):
        self.session.logger.warn("Logging In")

        self.stage = True

        headers = {
            "host": "accounts.zalando.com",
            "connection": "keep-alive",
            "cache-control": "max-age=0",
            "sec-ch-ua": self.sec_ch_ua,
            "x-csrf-token": self.csrf_token,
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "accept": "application/json",
            "x-flow-id": self.flow_id,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "origin": "https://accounts.zalando.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": self.login_url,
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        self.solver.solve_pixel(self.pixel_url, self.pixel_id)
        self.solver.solve(dynamic=True, special_mode=True)

        while True:
            response = self.session.get(
                f"https://accounts.zalando.com/api/login/schema",
                headers=headers,
                timeout=60
            )

            if response:
                break
        
        headers = {
            "host": "accounts.zalando.com",
            "connection": "keep-alive",
            "sec-ch-ua": self.sec_ch_ua,
            "x-csrf-token": self.csrf_token,
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "content-type": "application/json",
            "accept": "application/json",
            "x-flow-id": self.flow_id,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "origin": "https://accounts.zalando.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": self.login_url,
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        payload = {
            "email": self.task["ACCOUNT_EMAIL"],
            "request" :self.request,
            "secret": self.task["ACCOUNT_PASSWORD"]
        }

        while True:
            response = self.session.post(
                f"https://accounts.zalando.com/api/login",
                headers=headers,
                data=json.dumps(payload, separators=(",", ":")),
                timeout=60
            )

            if response:
                try:
                    parsed = json.loads(response.text)

                    if parsed["status"]:
                        self.session.logger.success("Succesfully Logged In")

                        self.stage = False

                        return True
                    
                    else:
                        self.session.logger.error("Error Logging In: Invalid Account")
                        time.sleep(getRetryDelay())
                        continue
                except:
                    self.session.logger.error("Error Logging In")
                    time.sleep(getRetryDelay())
                    continue

    def carting(self):
        self.session.logger.warn("Adding To Cart")

        headers = {
            "sec-ch-ua": self.sec_ch_ua,
            "x-zalando-experiments": f"{str(uuid.uuid4())}=THE_LABEL_IS_ENABLED;{str(uuid.uuid4())}=fdbe-release1-enabled;{str(uuid.uuid4())}=ABB_DISABLED",
            "x-xsrf-token": self.session.cookies["frsx"],
            "x-zalando-feature": "pdp",
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "content-type": "application/json",
            "viewport-width": "1920",
            "dpr": "1",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "accept": "*/*",
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": self.task["URL"],
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        payload = [{
            "id": "e7f9dfd05f6b992d05ec8d79803ce6a6bcfb0a10972d4d9731c6b94f6ec75033",
            "variables": {
                "addToCartInput": {
                    "productId": self.choosen["sku"],
                    "clientMutationId": "addToCartMutation"
                }
            }
        }]

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/graphql/add-to-cart/",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                try:
                    parsed = json.loads(response.text)

                    if parsed[0]["data"]["addToCart"]["__typename"] == "AddToCartPayload":
                        self.session.logger.success("Succesfully Added To Cart")

                        self.titelbar("carts")

                        break

                    else:
                        self.session.logger.error("Error Adding To Cart")
                        time.sleep(getRetryDelay())
                        continue
                except:
                    self.session.logger.error("Error Adding To Cart")
                    time.sleep(getRetryDelay())
                    continue

    def preload(self):
        self.session.logger.warn("Preloading Session")
    
        headers = {
            "sec-ch-ua": self.sec_ch_ua,
            "x-zalando-experiments": f"{str(uuid.uuid4())}=THE_LABEL_IS_ENABLED;{str(uuid.uuid4())}=fdbe-release1-enabled;{str(uuid.uuid4())}=ABB_DISABLED",
            "x-xsrf-token": self.session.cookies["frsx"],
            "x-zalando-feature": "pdp",
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "content-type": "application/json",
            "viewport-width": "1920",
            "dpr": "1",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "accept": "*/*",
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": self.task["URL"],
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        payload = [{
            "id": "e7f9dfd05f6b992d05ec8d79803ce6a6bcfb0a10972d4d9731c6b94f6ec75033",
            "variables": {
                "addToCartInput": {
                    "productId": random.choice(constants.PRELOAD["Zalando"]),
                    "clientMutationId": "addToCartMutation"
                }
            }
        }]

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/graphql/add-to-cart/",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                try:
                    parsed = json.loads(response.text)

                    if parsed[0]["data"]["addToCart"]["__typename"] == "AddToCartPayload":
                        self.session.logger.success("Succesfully Preloaded Session")

                        break

                    else:
                        self.session.logger.error("Error Preloading Session")
                        time.sleep(getRetryDelay())
                        continue
                except:
                    self.session.logger.error("Error Preloading Session")
                    time.sleep(getRetryDelay())
                    continue

    def cart(self):
        self.session.logger.warn("Checking Cart")

        headers = {
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": self.sec_ch_ua,
            "x-xsrf-token":	self.session.cookies["frsx"],
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "viewport-width": "848",
            "content-type": "application/json",
            "accept": "application/json",
            "dpr": "1",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://{self.domain}/nike-performance-everyday-cush-crew-3-pack-sports-socks-whiteblack-n1244d06l-a11.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/cart-gateway/carts",
                headers=headers,
                json={},
                timeout=60
            )

            if response:
                try:
                    parsed = json.loads(response.text)

                    self.items = []
                    if parsed["groups"]:
                        for group in parsed["groups"]:
                            for item in group["articles"]:
                                self.items.append(item["simple_sku"])
                    
                    if parsed["unavailable_articles"]:
                        for out_of_stock in parsed["unavailable_articles"]:
                            self.items.append(out_of_stock["simple_sku"])
                    
                    self.cart_id = parsed["id"]

                    self.session.logger.success(f"Succesfully Checked Cart: [{str(len(self.items))}] Items Found")
                    break
                except:
                    self.session.logger.error("Error Checking Cart")
                    time.sleep(getRetryDelay())
                    continue

    def clear_cart(self, size_pid):
        self.session.logger.warn(f"Clearing Item [{size_pid}]")

        headers = {
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": self.sec_ch_ua,
            "x-xsrf-token":	self.session.cookies["frsx"],
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "viewport-width": "848",
            "content-type": "application/json",
            "accept": "application/json",
            "dpr": "1",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://{self.domain}/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.delete(
                f"https://{self.domain}/api/cart-gateway/carts/{self.cart_id}/items/{size_pid}",
                headers=headers,
                json={},
                timeout=60
            )

            if response:
                self.session.logger.success(f"Succesfully Cleared [{size_pid}] From Cart")
                break

    def scrape_address_data(self):
        headers = {
            "cache-control": "max-age=0",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/checkout/address",
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    self.address_id = response.text.split('&quot;id&quot;:&quot;')[1].split('&quot;')[0]
                    break
                except:
                    self.session.logger.error("Error No Address Found In Account")
                    time.sleep(getRetryDelay())
                    continue

    def shipping(self):
        self.session.logger.warn("Submitting Shipping")

        headers = {
            "sec-ch-ua": self.sec_ch_ua,
            "x-zalando-footer-mode": "desktop",
            "x-xsrf-token":	self.session.cookies["frsx"],
            "sec-ch-ua-mobile": "?0",
            "x-zalando-header-mode": "desktop",
            "user-agent": self.user_agent,
            "x-zalando-checkout-app": "web",
            "content-type": "application/json",
            "accept": "application/json",
            "x-checkout-type-uuid":	str(uuid.uuid4()),
            "sec-ch-ua-platform": f'"{self.platform}"',
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://{self.domain}/checkout/address",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        payload = {
            "isDefaultShipping": True,
            "isDefaultBilling": True
        }

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/checkout/address/{self.address_id}/default",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                self.session.logger.success("Succesfully Submitted Shipping")
                break

    def scrape_payment_data(self):
        headers = {
            "cache-control": "max-age=0",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/checkout/payment",
                headers=headers,
                timeout=60
            )

            if response:
                self.jwt = response.text.split("purchaseSessionToken&quot;:&quot;")[1].split("&quot;,&")[0]
                self.purchase_session = response.text.split("purchaseSessionUrl&quot;:&quot;")[1].split("&quot;,")[0]

                break

    def payment(self):
        self.session.logger.warn("Submitting Payment")

        headers = {
            "Host": "purchase-session.client-api.payment.zalando.com",
            "Connection": "keep-alive",
            "sec-ch-ua": self.sec_ch_ua,
            "Content-Type": "application/json",
            "Accept-Language": "en-GB",
            "sec-ch-ua-mobile": "?0",
            "Authorization": f"Bearer {self.jwt}",
            "User-Agent": self.user_agent,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "Accept": "*/*",
            "Origin": f"https://{self.domain}",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://{self.domain}/",
            "Accept-Encoding": "gzip, deflate, br"
        }

        payload = {
            "payment_method_id": "paypal"
        }

        while True:
            response = self.session.post(
                self.purchase_session,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                parsed = json.loads(response.text)

                if parsed["payment_variant"]["payment_process_type"] == "PAYPAL":
                    self.session.logger.success("Succesfully Submitted Payment")
                    break

                else:
                    self.session.logger.error("Error Submitting Payment")
                    time.sleep(getRetryDelay())
                    continue

    def order(self):
        self.session.logger.warn("Submitting Order")

        headers = {
            "sec-ch-ua": self.sec_ch_ua,
            "x-zalando-footer-mode": "desktop",
            "x-xsrf-token":	self.session.cookies["frsx"],
            "sec-ch-ua-mobile": "?0",
            "x-zalando-header-mode": "desktop",
            "user-agent": self.user_agent,
            "x-zalando-checkout-app": "web",
            "content-type": "application/json",
            "accept": "application/json",
            "x-checkout-type-uuid":	str(uuid.uuid4()),
            "sec-ch-ua-platform": f'"{self.platform}"',
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://{self.domain}/checkout/confirm",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        payload = {
            "checkoutId": None,
            "eTag": None
        }


        while True:
            payload["checkoutId"] = self.checkout_id
            payload["eTag"] = self.eTag

            response = self.session.post(
                f"https://{self.domain}/api/checkout/buy-now",
                headers=headers,
                data=json.dumps(payload, separators=(",", ":")),
                timeout=60
            )

            if response:
                if "/cart" in response.url:
                    self.session.logger.warn("Waiting For Restock")
                    time.sleep(getMonitorDelay())
                    continue

                else:
                    try:
                        parsed = json.loads(response.text)

                        if "www.paypal.com" in parsed["url"]:
                            self.session.logger.success("Succesfully Checked Out")

                            self.titelbar("-carts")
                            self.titelbar("success")
                            try:
                                webhook_public({
                                    "Store": f"||ZALANDO {self.task['DOMAIN']}||",
                                    "Product": self.product_name,
                                    "Price": "Unknown",
                                    "Payment Method": "PayPal",
                                    "Size": self.choosen["size"],
                                    "User":"<@" +  str(self.task["discordid"]) + ">",
                                    },
                                    img=self.product_image,
                                    url=self.task["URL"],
                                )

                                webhook_private({
                                    "Store": f"||ZALANDO {self.task['DOMAIN']}||",
                                    "Product":self.product_name,
                                    "Price": "Unknown",
                                    "Payment Method":"PayPal",
                                    "Account": f"||{self.task['ACCOUNT_EMAIL']}:{self.task['ACCOUNT_PASSWORD']}||",
                                    "Size": self.choosen["size"]
                                    },
                                    img=self.product_image,
                                    success=True,
                                    profile_webhook=self.task["WEBHOOK"],
                                    product_url=self.task["URL"],
                                    url=generateUrl(self.session, parsed["url"])
                                )
                            except:
                                self.session.logger.error(f"Error Sending Webhook: Url [{parsed['url']}]")

                            return True
                        else:
                            self.session.logger.error("Error Checking Out")
                            time.sleep(getRetryDelay())
                            continue
                    except:
                        self.session.logger.error("Error Checking Out")
                        time.sleep(getRetryDelay())
                        continue

    def scrape_checkout_data(self):
        headers = {
            "cache-control": "max-age=0",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/checkout/confirm",
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    self.checkout_id = response.text.split("checkoutId&quot;:&quot;")[1].split("&quot;,")[0]
                    self.eTag = response.text.split("eTag&quot;:&quot;\&quot;")[1].split("\&quot;&quot;,")[0]
                except:
                    self.session.logger.error("Error Scraping Checkout Data")
                    time.sleep(getRetryDelay())
                    continue

                try:
                    self.product_name = response.text.split(";,&quot;name&quot;:&quot;")[1].split("&quot;,&quot;brandName&quot;:")[0]
                except:
                    self.product_name = "Unknown"
                                
                try:
                    self.product_image = response.text.split("imageUrl&quot;:&quot;")[1].split("?imwidth=")[0]
                except:
                    self.product_image = "https://mosaic02.ztat.net/nvt/z-header-fragment/zalando-logo/logo_default.svg"                    
                
                break

    def handle_checkout(self):
        headers = {
            "cache-control": "max-age=0",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/checkout/confirm",
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    if "checkout/address" in response.url:
                        self.scrape_address_data()
                        self.shipping()

                        return True
            
                    elif "checkout/payment" in response.url:
                        self.scrape_payment_data()
                        self.payment()

                        return True
            
                    elif "checkout/confirm" in response.url:
                        return True
                    
                    else:
                        self.session.logger.error("Error Handling Checkout")
                        time.sleep(getRetryDelay())
                        continue
                except:
                    self.session.logger.error("Error Handling Checkout")
                    time.sleep(getRetryDelay())
                    continue

    def injection(self, session : SpaceScraper, response : requests.Response):
        if response.status_code == 404:
            self.session.logger.error("Page Not Found [404]")
            time.sleep(getRetryDelay())

            return None
        
        elif response.status_code == 429:
            self.session.logger.error("Rate Limited [429]")
            self.session.set_proxy(switch=True)

            return None
        
        elif response.status_code == 403:
            self.session.logger.error("Access Denied [403]")
            self.session.set_proxy(switch=True)

            if self.stage:
                self.solver.solve(dynamic=True, special_mode=True)
            else:
                self.instance.solve(dynamic=False, special_mode=None)

            return None
                
        elif str(response.status_code).startswith("5"):
            self.session.logger.error(f"Server Error [{response.status_code}]")
            time.sleep(getRetryDelay())

            return None
        
        else:
            return response
    
    def setUpProductPage(self):
        self.session.logger.warn("Adding To Cart [Exclusive]")

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,ko;q=0.8",
            "cache-control": "max-age=0",
            "referer": self.task["URL"],
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent
        }

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/graphql/exclusive-add-to-cart/",
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    if '"exclusiveAddToCart": null' in response.text:
                        self.session.logger.error("Error Adding To Cart [Exclusive]")
                        time.sleep(getRetryDelay())
                        continue

                    elif "TOO_MANY_REQUESTS" in response.text:
                        self.session.logger.error("Error Adding To Cart [Exclusive]")
                        time.sleep(getRetryDelay())
                        continue

                    else:
                        self.session.logger.success("Succesfully Added To Cart")

                        self.titelbar("carts")

                        return True
                except:
                    self.session.logger.error("Error Adding To Cart [Exclusive]")
                    time.sleep(getRetryDelay())
                    continue

    def exclusiveCarting(self):
        self.session.logger.warn("Adding To Cart [Exclusive]")

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,ko;q=0.8",
            "content-type": "application/json",
            "dpr": "1",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "viewport-width": "1920",
            "x-xsrf-token": self.session.cookies["frsx"],
            "x-zalando-add-to-cart-sku": self.choosen["sku"],
            "x-zalando-experiments": f"{str(uuid.uuid4())}=THE_LABEL_IS_ENABLED;{str(uuid.uuid4())}=fdbe-release1-enabled;{str(uuid.uuid4())}=ABB_DISABLED",
            "x-zalando-feature": "pdp",
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.user_agent,
            "content-type": "application/json",
            "origin": f"https://{self.domain}",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": self.task["URL"],
            "accept-encoding": "gzip, deflate, br"
        }

        payload = [{
            "id": "f6b32c4d13074e5de69f24664c75ebc7b72e89b842aa1b68dd88e02ba9a4aacb",
            "variables": {
                "exclusiveAddToCartInput": {
                    "clientMutationId": "exclusiveAddToCartMutation",
                    "productId": self.choosen["sku"]
                }
            }
        }]

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/graphql/exclusive-add-to-cart/",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                try:
                    if '"exclusiveAddToCart": null' in response.text:
                        self.session.logger.error("Error Adding To Cart [Exclusive]")
                        time.sleep(getRetryDelay())
                        continue

                    elif "TOO_MANY_REQUESTS" in response.text:
                        self.session.logger.error("Error Adding To Cart [Exclusive]")
                        time.sleep(getRetryDelay())
                        continue

                    else:
                        self.session.logger.success("Succesfully Added To Cart")

                        self.titelbar("carts")

                        return True
                except:
                    self.session.logger.error("Error Adding To Cart [Exclusive]")
                    time.sleep(getRetryDelay())
                    continue

    def exclusiveConfirm(self):
        self.session.logger.warn("Confirm [Exclusive]")

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,ko;q=0.8",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "viewport-width": "1920",
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/exclusive/checkout/confirm",
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    self.checkout_id = response.text.split("checkoutId&quot;:&quot;")[1].split("&quot;,")[0]
                    self.eTag = response.text.split("eTag&quot;:&quot;\&quot;")[1].split("\&quot;&quot;,")[0]
                except:
                    self.session.logger.error("Error Scraping Checkout Data")
                    time.sleep(getRetryDelay())
                    continue

                try:
                    self.product_name = response.text.split(";,&quot;name&quot;:&quot;")[1].split("&quot;,&quot;brandName&quot;:")[0]
                except:
                    self.product_name = "Unknown"
                                
                try:
                    self.product_image = response.text.split("imageUrl&quot;:&quot;")[1].split("?imwidth=")[0]
                except:
                    self.product_image = "https://mosaic02.ztat.net/nvt/z-header-fragment/zalando-logo/logo_default.svg"                    
                
                break

    def exclusiveBuyNow(self):
        self.session.logger.warn("Buy-Now [Exclusive]")

        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": f"https://{self.domain}",
            "referer": self.task["URL"],
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.user_agent,
            "x-xsrf-token": self.session.cookies["frsx"],
            "x-zalando-checkout-app": "web",
            "x-zalando-footer-mode": "desktop",
            "x-zalando-header-mode": "desktop"
            # il manque peut-être une requête avec le "x-checkout-type-uuid": faut tester si ça marche sans, je l'avais fait sans dans l'extension
        }

        payload = [{
            "checkoutId": self.checkout_id, # Il faut les récupéré normalment le Etag et le checkoutId est dans la réponse de la requête "/exclusive/checkout/confirm"
            "eTag": self.eTag # Voila comment les Récup : checkoutId = e.split("checkoutId&quot;:&quot;")[1].split("&quot")[0];
            # eTag = e.split("eTag&quot;:&quot;\\&quot;")[1].split('\\')[0];
            # It's inside the html code given by the "/exclusive/checkout/confirm" request 
            # It's Done V
        }]

        while True:
            response = self.session.post(
                f"https://{self.domain}/api/exclusive/checkout/buy-now",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response:
                try:
                    if '"exclusiveAddToCart": null' in response.text:
                        self.session.logger.error("Error Buying [Exclusive]")
                        time.sleep(getRetryDelay())
                        continue

                    elif "TOO_MANY_REQUESTS" in response.text:
                        self.session.logger.error("Error Buying [Exclusive]")
                        time.sleep(getRetryDelay())
                        continue

                    else:
                        self.session.logger.success("Succesfully Bought [Exclusive]")

                        print(response.text) #We are supposed to get the paypal link here
                        self.titelbar("carts")

                        return True
                except:
                    self.session.logger.error("Error Buying [Exclusive]")
                    time.sleep(getRetryDelay())
                    continue

    def initialise(self):
        self.session.logger.warn("Initializing Session [2]")

        headers = {
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                f"https://{self.domain}/myaccount",
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    endpoint = response.text.split('type="text/javascript"  src="')[1].split('">')[0]

                    self.instance.set_endpoint(
                        f"https://{self.domain}{endpoint}"
                    )

                    self.pixel_id = re.findall(r'<script >bazadebezolkohpepadr="(.*?)"</script>', response.text)[0]
                    self.pixel_url_split = re.findall(r'</script><script type="text/javascript" src="(.*?)"  defer></script></head>', response.text)[0].split("13/")[1]
                    self.pixel_url = f"https://{self.domain}/akam/13/pixel_{self.pixel_url_split}"

                    self.instance.solve_pixel(self.pixel_url, self.pixel_id)
                    self.instance.solve(dynamic=False, special_mode=None)

                    self.session.logger.success("Succesfully Initialized Session [2]")

                    return True
                except:
                    self.session.logger.error("Error Initializing Session [2]")
                    time.sleep(getRetryDelay())
                    continue
    
    def monitor(self):
        self.session.logger.warn("Monitoring Product")

        headers = {
            "cache-control": "max-age=0",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self.platform}"',
            "upgrade-insecure-requests": "1",
            "user-agent": self.user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        while True:
            response = self.session.get(
                self.task["URL"],
                headers=headers,
                timeout=60
            )

            if response:
                try:
                    scraper = json.loads(response.text.split('"simples":')[1].split(',"condition":')[0])

                    instock = [s for s in scraper if s["offer"]["stock"]["quantity"] != "OUT_OF_STOCK"]

                    if len(instock) == 0:
                        self.session.logger.warn("Waiting For Restock")
                        time.sleep(getMonitorDelay())
                        continue

                    else:
                        if "random" in self.task["SIZE"]:
                            sizes = [s for s in instock]

                            self.choosen = random.choice(sizes)

                            self.session.logger.success(f"Succesfully Got Sizes [EU {self.choosen['size']}]")

                            return True
                        
                        else:
                            sizes = [s for s in instock if s["size"] in self.task["SIZE"]]

                            if len(sizes) == 0:
                                self.session.logger.warn("Waiting For Restock")
                                time.sleep(getMonitorDelay())
                                continue

                            else:
                                self.choosen = random.choice(sizes)

                                self.session.logger.success(f"Succesfully Got Sizes [EU {self.choosen['size']}]")

                                return True
                except:
                    self.session.logger.error("Error Monitoring Product")
                    time.sleep(getRetryDelay())
                    continue
