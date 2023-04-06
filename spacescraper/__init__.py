# ------------------------------------------------------------------------------- #

import logging
import platform
import traceback
from .log import Logger
import re
import base64
import random
import requests
import sys
import ssl
import os
import time
try:
    from src.functions.settings import getRetryDelay, getMonitorDelay, getPath,resource_path
except Exception:
    getMonitorDelay = lambda:  3
    getRetryDelay = lambda: 5
    getPath = lambda: "."


from copy import deepcopy

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from requests_toolbelt.utils import dump

from time import sleep
from bs4 import BeautifulSoup
import numpy as np
import json

# ------------------------------------------------------------------------------- #

try:
    import brotli
except ImportError:
    pass

import copyreg
from urllib.parse import urlparse, urljoin

from .user_agent import User_Agent
from .datadome.magicnumber import DatadomeMagicNumber
from .adyen import Encryptor, Fingerprint

from .exceptions import (
    CSRF_Exception,
    FormKey_Exception,
    GetInput_Exception
)

# ------------------------------------------------------------------------------- #

__version__ = '0.5.1'

# ------------------------------------------------------------------------------- #

class TLSAdapter(HTTPAdapter):

    __attrs__ = [
        'ssl_context',
        'max_retries',
        'config',
        '_pool_connections',
        '_pool_maxsize',
        '_pool_block',
        'source_address'
    ]

    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        self.cipherSuite = kwargs.pop('cipherSuite', None)
        self.source_address = kwargs.pop('source_address', None)

        if self.source_address:
            if isinstance(self.source_address, str):
                self.source_address = (self.source_address, 0)

            if not isinstance(self.source_address, tuple):
                raise TypeError(
                    "source_address must be IP address string or (ip, port) tuple"
                )

        if not self.ssl_context:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.ssl_context.set_ciphers(self.cipherSuite)
            self.ssl_context.set_ecdh_curve('prime256v1')
            self.ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)

        super(TLSAdapter, self).__init__(**kwargs)

    # ------------------------------------------------------------------------------- #

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        kwargs['source_address'] = self.source_address
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

    # ------------------------------------------------------------------------------- #

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        kwargs['source_address'] = self.source_address
        return super(TLSAdapter, self).proxy_manager_for(*args, **kwargs)

# ------------------------------------------------------------------------------- #

class SpaceScraper(Session):
    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop('debug', False)
        self.delay = kwargs.pop('delay', None)
        self.cipherSuite = kwargs.pop('cipherSuite', None)
        self.ssl_context = kwargs.pop('ssl_context', None)
        self.captcha = kwargs.pop('captcha', {'provider': 'vanaheim'})
        self.requestPreHook = kwargs.pop('requestPreHook', self.preinjection)
        self.requestPostHook = kwargs.pop('requestPostHook', self.injection)
        self.source_address = kwargs.pop('source_address', None)

        # Identify Task
        self.module_name = kwargs.pop('module_name', None)
        self.taskcount = kwargs.pop('taskcount', None)
        self.max_errors = kwargs.pop('max_errors', None)
        self.errors = 0

        # Proxy
        self.proxyList = kwargs.pop('proxyList', None)

        # Logger
        self.logger = Logger(self.module_name,self.taskcount)

        self.allow_brotli = kwargs.pop(
            'allow_brotli',
            True if 'brotli' in sys.modules.keys() else False
        )

        self.user_agent = User_Agent(
            allow_brotli=self.allow_brotli,
            browser=kwargs.pop('browser', {
                'browser': 'chrome',
                'mobile': False,
                'platform': 'windows'
            })
        )

        super(SpaceScraper, self).__init__(*args, **kwargs)

        self.set_proxy()

        if 'requests' in self.headers['User-Agent']:
            # ------------------------------------------------------------------------------- #
            # Set a random User-Agent if no custom User-Agent has been set
            # ------------------------------------------------------------------------------- #
            self.headers = self.user_agent.headers
            if not self.cipherSuite:
                self.cipherSuite = self.user_agent.cipherSuite

        if isinstance(self.cipherSuite, list):
            self.cipherSuite = ':'.join(self.cipherSuite)

        self.mount(
            'https://',
            TLSAdapter(
                cipherSuite=self.cipherSuite,
                ssl_context=self.ssl_context,
                source_address=self.source_address
            )
        )

        # purely to allow us to pickle dump
        copyreg.pickle(ssl.SSLContext, lambda obj: (obj.__class__, (obj.protocol,)))

    
    # ------------------------------------------------------------------------------- #
    # Allow us to pickle our session back with all variables
    # ------------------------------------------------------------------------------- #

    def __getstate__(self):
        return self.__dict__
    
    # ------------------------------------------------------------------------------- #
    # Allow replacing actual web request call via subclassing
    # ------------------------------------------------------------------------------- #

    def perform_request(self, method, url, *args, **kwargs):
        return super(SpaceScraper, self).request(method, url, *args, **kwargs)
    
    # ------------------------------------------------------------------------------- #
    # debug the request via the response
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def debugRequest(req):
        try:
            print(dump.dump_all(req).decode('utf-8', errors='backslashreplace'))
        except ValueError as e:
            print(f"Debug Error: {getattr(e, 'message', e)}")
    
    # ------------------------------------------------------------------------------- #
    # Raise an Exception with no stacktrace.
    # ------------------------------------------------------------------------------- #
    
    @staticmethod
    def raiseException(exception, msg):
        sys.tracebacklimit = 0
        raise exception(msg)
    
    # ------------------------------------------------------------------------------- #
    # Decode Brotli on older versions of urllib3 manually
    # ------------------------------------------------------------------------------- #

    def decodeBrotli(self, resp):
        if requests.packages.urllib3.__version__ < '1.25.1' and resp.headers.get('Content-Encoding') == 'br':
            if self.allow_brotli and resp._content:
                resp._content = brotli.decompress(resp.content)
            else:
                logging.warning(
                    f'You\'re running urllib3 {requests.packages.urllib3.__version__}, Brotli content detected, '
                    'Which requires manual decompression, '
                    'But option allow_brotli is set to False, '
                    'We will not continue to decompress.'
                )

        return resp

    # ------------------------------------------------------------------------------- #
    # request function
    # ------------------------------------------------------------------------------- #
    
    def request(self, method, url, *args, **kwargs):
        # pylint: disable=E0203
        if kwargs.get('proxies') and kwargs.get('proxies') != self.proxies:
            self.proxies = kwargs.get('proxies')

        # ------------------------------------------------------------------------------- #
        # Pre-Hook the request via user defined function.
        # ------------------------------------------------------------------------------- #

        if self.requestPreHook:
            (method, url, args, kwargs) = self.requestPreHook(
                method,
                url,
                *args,
                **kwargs
            )

        # ------------------------------------------------------------------------------- #
        # Make the request via requests.
        # ------------------------------------------------------------------------------- #
        try:
            response = self.decodeBrotli(
                self.perform_request(method, url, *args, **kwargs)
            )
        except requests.exceptions.HTTPError:
            self.logger.error(f'ERROR: HTTP Error',log_message=f"HTTPError : {traceback.format_exc()}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        except requests.exceptions.InvalidURL:
            self.logger.error(f'ERROR: Invalid URL',log_message=f"InvalidURL : {traceback.format_exc()}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        except requests.exceptions.ProxyError:
            self.logger.error(f'ERROR: Proxy Error -> switching proxy',log_message=f"ProxyError : {traceback.format_exc()}")
            self.checkErrors()
            self.set_proxy(switch=True)
            sleep(getRetryDelay())
            return None
        except requests.exceptions.TooManyRedirects:
            self.logger.error(f'ERROR: Too Many Redirects',log_message=f"TooManyRedirects : {traceback.format_exc()}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f'ERROR: Connection Error', log_message=f"ConnectionError : {traceback.format_exc()}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        except requests.exceptions.Timeout:
            self.logger.error(f'ERROR: Timeout', log_message=f"Timeout : {traceback.format_exc()}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        except Exception:
            if "asos-identity://auth/#id_token=" in str(traceback.format_exc()):
                return str(traceback.format_exc())
            self.logger.error(f'ERROR: Unknown Error', log_message=f"UnknownError : {traceback.format_exc()}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None

        # ------------------------------------------------------------------------------- #
        # Debug the request via the Response object.
        # ------------------------------------------------------------------------------- #

        if self.debug:
            self.debugRequest(response)

        # ------------------------------------------------------------------------------- #
        # Post-Hook the request aka Post-Hook the response via user defined function.
        # ------------------------------------------------------------------------------- #

        if self.requestPostHook:
            response = self.requestPostHook(self, response)

            if self.debug:
                self.debugRequest(response)
        
        return response

    # ------------------------------------------------------------------------------- #
    # Function for prettifying a response text.
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def prettify(res):
        soup = BeautifulSoup(res,'html.parser')
        soup.prettify()
        return soup
    
    # ------------------------------------------------------------------------------- #
    # Function for returning a json response text.
    # ------------------------------------------------------------------------------- #
    
    @staticmethod
    def jsonify(res):
        return json.loads(res)
    

    # ------------------------------------------------------------------------------- #
    # Functions for Base64 encoding / decoding
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def b64encode(string : str):
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def b64decode(string : str):
        return base64.b64decode(string).decode('utf-8')

    # ------------------------------------------------------------------------------- #
    # Function for scraping a needed csrf-token.
    # ------------------------------------------------------------------------------- #
    
    @staticmethod
    def get_csrf_token(response : requests.Response):
        try:
            soup = SpaceScraper.prettify(response.text)
            csrf_token = soup.find('input',{'name':re.compile('csrf')}).get('value')
            return csrf_token
        except Exception:
            pass
        try:
            return response.cookies['csrf-token']
        except KeyError:
            pass
        SpaceScraper.raiseException(CSRF_Exception,'Unable to find csrf-token in given response!')
    
    # ------------------------------------------------------------------------------- #
    # Function for scraping a needed form-key.
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def get_form_key(soup):
        try:
            form_key = soup.find('input',{'name':'form_key'}).get('value')
            return form_key
        except Exception:
            pass
        SpaceScraper.raiseException(FormKey_Exception,'Unable to find form-key in given response!')
    
    # ------------------------------------------------------------------------------- #
    # Function for scraping a needed input.
    # ------------------------------------------------------------------------------- #
    
    @staticmethod
    def get_input(soup,attr,value):
        try:
            input = soup.find('input',{attr:value}).get('value')
            return input
        except Exception:
            pass
        SpaceScraper.raiseException(GetInput_Exception,'Unable to find the requested input in given response!')

    # ------------------------------------------------------------------------------- #
    # Functions for finding specific links in the html.
    # ------------------------------------------------------------------------------- #
    
    @staticmethod
    def find_all_jpgs(text: str, domain: str) -> list:
        pattern = re.compile(r'"([^=\s,:()]*?\.jpg[^\s]*?)"', re.IGNORECASE)
        jpgs = re.findall(pattern,text)
        return [jpg if jpg.startswith('http') else f"https://{domain}{jpg}" for jpg in jpgs]

    @staticmethod
    def find_all_pngs(text: str, domain: str) -> list:
        pattern = re.compile(r'"([^=\s,:()]*?\.png[^\s]*?)"', re.IGNORECASE)
        pngs = re.findall(pattern,text)
        return [png if png.startswith('http') else f"https://{domain}{png.replace('//','/')}" for png in pngs]

    @staticmethod
    def find_all_svgs(text: str, domain: str) -> list:
        pattern = re.compile(r'"([^=\s,:()]*?\.svg)"', re.IGNORECASE)
        svgs = re.findall(pattern,text)
        return [svg if svg.startswith('http') else f"https://{domain}{svg.replace('//','/')}" for svg in svgs]

    @staticmethod
    def find_all_csss(text: str, domain: str) -> list:
        pattern = re.compile(r'"([^=\s,:()]*?\.css)"', re.IGNORECASE)
        csss = re.findall(pattern,text)
        return [css if css.startswith('http') else f"https://{domain}{css.replace('//','/')}" for css in csss]

    @staticmethod
    def find_all_gifs(text: str, domain: str) -> list:
        pattern = re.compile(r'"([^=\s,:()]*?\.gif)"', re.IGNORECASE)
        gifs = re.findall(pattern,text)
        return [gif if gif.startswith('http') else f"https://{domain}{gif.replace('//','/')}" for gif in gifs]

    @staticmethod
    def find_all_scripts(text: str, domain: str) -> list:
        soup = BeautifulSoup(text, 'html.parser')
        scripts = [script.get("src") for script in soup.find_all('script', {'type': 'text/javascript'}) if script.get("src")]
        pattern = re.compile(r'([^\s,:()]*?\.js)', re.IGNORECASE)
        regex_scripts = re.findall(pattern,text)

        for s in regex_scripts:
            s = s.replace('src="','').replace("'/","/")
            if not s.startswith('/') and not s.startswith("//") and not s.startswith("http"):
                continue
            scripts.append(s)

        for i, s in enumerate(scripts):
            if s.startswith('//'):
                scripts[i] = f"https:{s}"
            elif s.startswith('/'):
                scripts[i] = f"https://{domain}{s}"
            else:
                continue
            
        return list(dict.fromkeys(scripts))

    # ------------------------------------------------------------------------------- #
    # Function returning a sizelist from a sizes string given.
    # ------------------------------------------------------------------------------- #
    
    @staticmethod
    def get_sizes(sizes):
        if "-" in sizes and "," in sizes:
            sizeRanges = sizes.split(",")
            sizes = []
            for r in sizeRanges:
                min = float(r.split("-")[0])
                max = float(r.split("-")[1]) + 0.5
                sizeRange = np.arange(min,max,0.5)
                for s in sizeRange:
                    sizes.append(f"{s:g}")
            return sizes
        if "-" in sizes:
            min = float(sizes.split("-")[0])
            max = float(sizes.split("-")[1]) + 0.5
            sizeRange = np.arange(min,max,0.5)
            return [f'{s:g}' for s in sizeRange]
        elif "," in sizes:
            sizeRange = sizes.split(",")
            return sizeRange
        elif "r" in sizes or "" == sizes:
            return ""
        else:
            return [sizes]

    # ------------------------------------------------------------------------------- #
    # Function returning a random sizet from a sizes list given.
    # ------------------------------------------------------------------------------- #        
    
    @staticmethod
    def get_random_size(sizes: list):
        random.shuffle(sizes)
        return random.choice(sizes)

    # ------------------------------------------------------------------------------- #
    # Datadome
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def is_Datadome_Challenge(session,res):
        try:
            return (
                session.cookies["datadome"] is not None and
                (re.search('datadome',res.text, re.M | re.S) or re.search('geo.captcha-delivery.com',res.text, re.M | re.S)) and
                (re.search('t=fe',res.text, re.M | re.S) or re.search("'t':'fe'",res.text, re.M | re.S) or re.search('"t":"fe"',res.text, re.M | re.S))
            )
        except (AttributeError,KeyError):
            pass

        return False
    
    @staticmethod
    def is_Datadome_Block(session,res):
        try:
            return (
                session.cookies["datadome"] is not None and
                (re.search('datadome',res.text, re.M | re.S) or re.search('geo.captcha-delivery.com',res.text, re.M | re.S)) and
                (re.search('t=bv',res.text, re.M | re.S) or re.search("'t':'bv'",res.text, re.M | re.S) or re.search('"t":"bv"',res.text, re.M | re.S))
            )
        except (AttributeError,KeyError):
            pass

        return False
    
    @staticmethod
    def generate_magicnumber(cid,t,ua):
        return DatadomeMagicNumber(cid,t,ua).Generate()
        
    # ------------------------------------------------------------------------------- #
    # Adyen
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def adyen_encryptor(adyen_public_key, adyen_version='_0_1_8', adyen_prefix='adyenjs'):
        return Encryptor(adyen_public_key, adyen_version, adyen_prefix)
    
    @staticmethod
    def adyen_fingerprint(device=None):
        if device:
            device = device
        else:
            device = SpaceScraper.get_device()
        
        return Fingerprint(device).generateFingerprint()
    
    # ------------------------------------------------------------------------------- #
    # Devices
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def get_device():
        with open(resource_path('spacescraper/data/devices.json')) as devices_file:
            devices = json.load(devices_file)
            return random.choice(devices)
    
    # ------------------------------------------------------------------------------- #
    # UserAgent
    # ------------------------------------------------------------------------------- #
    @staticmethod
    def get_ua_platform(user_agent : str):
        if "Mac" in user_agent:
            return "macOS"
        elif "Windows" in user_agent:
            return "Windows"
        elif "Linux" in user_agent:
            return "Linux"
        elif "CrOS" in user_agent:
            return "Chrome OS"
        else:
            return "Unknown"
    
    @staticmethod
    def get_chrome_version(user_agent : str):
        return user_agent.split("Chrome/")[1].split(".")[0]
    
    @staticmethod
    def get_chrome_sec_ch_ua(version : str):
        if version > "106":
            return f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not=A?Brand";v="24"'
        elif version > "103":
            return f'"Google Chrome";v="{version}", "Not)A;Brand";v="8", "Chromium";v="{version}"'
        elif version > "100":
            return f'".Not/A)Brand";v="99", "Google Chrome";v="{version}", "Chromium";v="{version}"'
        else:
            return f'" Not A;Brand";v="99", "Chromium";v="{version}", "Google Chrome";v="{version}"'

    # ------------------------------------------------------------------------------- #
    # Standard Prepare Method
    # ------------------------------------------------------------------------------- #

    def preinjection(self, method, url, *args, **kwargs):
        if self.tls:
            if 'headers' in kwargs:
                self.headers = kwargs.pop("headers",self.headers)
                self.bifrost.headerOrder = [key for key in self.headers]
        return (method, url, args, kwargs)
    
    # ------------------------------------------------------------------------------- #
    # Check Error Count Method
    # ------------------------------------------------------------------------------- #

    def checkErrors(self):
        if self.max_errors:
            self.errors += 1
            if self.errors >= self.max_errors:
                self.logger.error('Max Error Count Reached!')
                sys.exit()
            
    # ------------------------------------------------------------------------------- #
    # Standard Injection Method
    # ------------------------------------------------------------------------------- #

    def injection(self, session : requests.Session, response :requests.Response):
        if SpaceScraper.is_Datadome_Block(session, response):
            self.logger.warn("Datadome Block detected!")
            sleep(getRetryDelay())
            self.set_proxy(switch=True)
            return None
        elif response.status_code == 400:
            self.logger.error("Bad Request Error: 400", log_message=f"Bad Request Error [400] [{response.url}] : {response.text}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        elif response.status_code == 403:
            self.logger.error("Forbidden Error: 403", log_message=f"Forbidden Error [403] [{response.url}] : {response.text}")
            self.checkErrors()
            self.set_proxy(switch=True)
            sleep(getRetryDelay())
            return None
        elif response.status_code == 404:
            self.logger.error("Not Found Error: 404", log_message=f"Not Found Error [404] [{response.url}] : {response.text}")
            self.checkErrors()
            sleep(getMonitorDelay())
            return None
        elif response.status_code == 429:
            self.logger.error("Ratelimit Error: 429", log_message=f"Ratelimit Error [429] [{response.url}] : {response.text}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        elif str(response.status_code).startswith("5"):
            self.logger.error(f"Server Error: {str(response.status_code)}", log_message=f"Server Error [{str(response.status_code)}] [{response.url}] : {response.text}")
            self.checkErrors()
            sleep(getRetryDelay())
            return None
        else:
            return response
    
    # ------------------------------------------------------------------------------- #
    # Proxy Method
    # ------------------------------------------------------------------------------- #

    def set_proxy(self,proxyList:list=None,switch:bool=False):
        """
        Sets or updates the proxy of the current session
        :param session -> current session
        :param proxyList -> proxy list
        :param switch -> True if session already has a proxy set
        """
        if self.proxyList is not None and proxyList is None:
            proxyList = self.proxyList

        if switch == True and proxyList != None:
            self.logger.warn("Switching proxy")
            self.proxies.clear()
        try:
            if proxyList != None:
                proxy = random.choice(proxyList)
                proxy = proxy.replace("\n", "")
                https = proxy.split(':')
                try:
                    ip = https[0]
                    port = https[1]
                    user = https[2]
                    passw = https[3]
                    FormattedProxy = {
                        'http': 'http://' + str(user) + ':' + str(passw) + '@' + str(ip) + ':' + str(port),
                        'https': 'http://' + str(user) + ':' + str(passw) + '@' + str(ip) + ':' + str(port),
                    }
                except IndexError:
                    ip = https[0]
                    port = https[1]
                    FormattedProxy = {
                        'http': str(ip) + ':' + str(port),
                        'https': str(ip) + ':' + str(port),
                    }
                self.proxies = FormattedProxy

        except Exception:
            self.logger.error("Error setting proxy")

    @classmethod
    def create_session(cls, sess=None, tls=False, client_hello=None, **kwargs):

        scraper = cls(**kwargs)

        if sess:
            for attr in ['auth', 'cert', 'cookies', 'headers', 'hooks', 'params', 'proxies', 'data']:
                val = getattr(sess, attr, None)
                if val:
                    setattr(scraper, attr, val)
        
        if tls:
            try:
                
                if client_hello:
                    scraper.bifrost.clientHello = client_hello
                else:
                    scraper.bifrost.clientHello = 'chrome'
            except Exception as e:
                print(e,traceback.format_exc())
                time.sleep(10)
                scraper.logger.error("Error loading tls library")
                tls = False
        
        scraper.tls = tls

        return scraper

# ------------------------------------------------------------------------------- #
