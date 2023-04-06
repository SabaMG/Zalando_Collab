#############################
# Title  :  SecuredTouch     #
# Author : 	Bwonderkid#2121 #
# Created: 	19.11.2022      #
# Updated: 	21.11.2022      #
#############################

#############################
# IMPORTS #
#############################
import gzip
import uuid
import json
import time
import random
from .exceptions import Unsupported_UserAgent_Exception
try:
    from src.functions.settings import getPath,resource_path
except Exception:
    getPath = lambda : "."
#############################

#############################
# VARIABLES #
#############################
PATH = resource_path('spacescraper/data/devices.json')
#############################

class SecuredTouch(object):

    T = "eG9yLWVuY3J5cHRpb24"
    """Encryption key used for the payload"""


    def __init__(self, appId: str, client_version: str, user_agent: str, location: str):
        """Initialize SecuredTouch object and attribiutes

        Args:
            appId (str): Application ID realted to the store
            client_version (str): Client version used on the website
            user_agent (str): User agent used in requests
            location (str): Location of the user on the website
        
        Example:
            SecuredTouch("asos", "3.13.2w","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36", "https://my.asos.com/identity/login")
        """
        self.appId = appId
        self.client_version = client_version
        self.device_id = str(uuid.uuid4())
        self.instance_id = str(uuid.uuid4())
        self.device = self.getDevice()
        self.user_agent = user_agent
        self.location = location
        self.device_type = self.get_device_type(self.user_agent)

    def starter(self):
        """Returns the compressed starter payload
        
        Returns:
            bytes: Payload
        """

        post_data = {
            "device_id": f"Id-{self.device_id}",
            "clientVersion": self.client_version,
            "deviceType": self.device_type,
            "authToken": "",
        }

        return gzip.compress(json.dumps(post_data).encode("utf-8"))
    
    def interactions(self, stToken, sessionId):
        """Returns the compressed interactions payload

        Args:
            stToken (str): SecuredTouch token got from starter
            sessionId (str): Session ID got from the website
        
        Returns:
            bytes: Payload
        """

        post_data = {
                "applicationId": self.appId,
                "deviceId": f"Id-{self.device_id}",
                "deviceType": self.device_type,
                "appSessionId": sessionId,
                "stToken": stToken,
                "keyboardInteractionPayloads": [],
                "mouseInteractionPayloads": [],
                "indirectEventsPayload": [],
                "indirectEventsCounters": {},
                "gestures": [],
                "metricsData": {},
                "accelerometerData": [],
                "gyroscopeData": [],
                "linearAccelerometerData": [],
                "rotationData": [],
                "index": 0,
                "payloadId": str(uuid.uuid4()),
                "tags": [{"name":f"location:{self.location}","epochTs":round(time.time() * 1000) + 10,"timestamp":round(time.time() * 1000) + 10}],
                "environment": {
                    "ops": 0,
                    "webGl": "",
                    "devicePixelRatio": self.device["window"]["devicePixelRatio"],
                    "screenWidth": self.device["screen"]["width"],
                    "screenHeight": self.device["screen"]["height"],
                },
                "isMobile": False,
                "usernameTs": round(time.time() * 1000),
                "username": f"Id-{self.device_id}",
            }
        
        compressed_data = gzip.compress(json.dumps(post_data).encode("utf-8"))
        encrypted_data = self.encrypt(compressed_data)
        return encrypted_data
    
    def metadata(self, sessionId):
        """Returns the compressed metadata payload

        Args:
            sessionId (str): Session ID got from the website
        
        Returns:
            bytes: Payload
        """

        post_data = {
            "deviceType":self.device_type,
            "deviceId":f"Id-{self.device_id}",
            "appSessionId":sessionId,
            "osVersion":f"{self.get_platform(self.user_agent)} {self.get_os_version(self.user_agent)}",
            "display":{
                "ops":0,
                "webGl":"",
                "devicePixelRatio":self.device["window"]["devicePixelRatio"],
                "screenWidth":self.device["screen"]["width"],
                "screenHeight":self.device["screen"]["height"],
                "availWidth":self.device["screen"]["availWidth"],
                "availHeight":self.device["screen"]["availHeight"],
                "width":self.device["screen"]["width"],
                "height":self.device["screen"]["height"],
                "colorDepth":self.device["screen"]["colorDepth"],
                "pixelDepth":self.device["screen"]["pixelDepth"],
                "availLeft":self.device["screen"]["availLeft"],
                "availTop":self.device["screen"]["availTop"],
                "onchange":None,
                "isExtended":False
                },
            "sensorsMetadata":{
                "DEDVCE_LIGHT_SUPPORTED":False,
                "IS_TOUCH_DEVICE":False,
                "PROXIMITY_SUPPORTED":False
                },
            "identificationMetadata":{
                "FINGER_PRINT":"c3f1202d7c42081b82675eb11cc42f12",
                "OS_NAME":self.get_platform(self.user_agent),
                "OS_VERSION":self.get_os_version(self.user_agent),
                "DEVICE_MODEL":"",
                "DEVICE_VENDOR":"",
                "BROWSER_ENGINE_NAME":"Blink",
                "BROWSER_ENGINE_VERSION":self.get_chrome_version(self.user_agent),
                "CPU_ARCHITECTURE":"",
                "NAVIGATOR_VENDOR":"Google Inc.",
                "NAVIGATOR_PLUGINS_LENGTH":5,
                "NAVIGATOR_MIME_TYPES_LENGTH":2,
                "NAVIGATOR_LANGUAGE":"de-DE",
                "NAVIGATOR_LANGUAGES.0":"de-DE",
                "NAVIGATOR_WEB_DRIVER":False,
                "NAVIGATOR_HARDWARE_CONCURRENCY":10,
                "NAVIGATOR_VIBRATE":True,
                "PUSH_NOTIFICATIONS_SUPPORTED":True,
                "NAVIGATOR_APP_CODE_NAME":"Mozilla",
                "NAVIGATOR_APP_NAME":"Netscape",
                "NAVIGATOR_APP_VERSION":self.user_agent.split("Mozilla/")[1],
                "NAVIGATOR_ON_LINE":True,
                "NAVIGATOR_PLATFORM":self.device["navigator"]["platform"],
                "NAVIGATOR_PRODUCT":"Gecko",
                "NAVIGATOR_USER_AGENT":self.user_agent,
                "NAVIGATOR_DEVICE_MEMORY":8,
                "NAVIGATOR_CONNECTION_RTT":50,
                "ambient_light":False,
                "application_cache":False,
                "audio":True,
                "audio.ogg":"probably",
                "audio.mp3":"probably",
                "audio.opus":"probably",
                "audio.wav":"probably",
                "audio.m4a":"maybe",
                "battery_api":True,
                "blob_constructor":True,
                "context_menu":False,
                "cors":True,
                "custom_elements":True,
                "custom_protocol_handler":True,
                "custom_event":True,
                "dart":False,
                "data_view":True,
                "event_listener":True,
                "force_touch":False,
                "full_screen":True,
                "game_pads":True,
                "geo_location":True,
                "ie8compat":False,
                "internationalization":True,
                "json":True,
                "ligatures":True,
                "media_source":True,
                "message_channel":True,
                "notification":True,
                "page_visibility":True,
                "performance":True,
                "pointer_events":True,
                "pointer_lock":True,
                "query_selector":True,
                "quota_management":True,
                "request_animation_frame":True,
                "service_worker":True,
                "touch_events":True,
                "typed_arrays":True,
                "vibrate":True,
                "video":True,
                "video.ogg":"probably",
                "video.h264":"probably",
                "video.h265":"",
                "video.webm":"probably",
                "video.vp9":"probably",
                "video.hls":"",
                "video.av1":"",
                "web_gl":True,
                "web_sockets":True,
                "x_domain_request":False,
                "matchmedia":True,
                "JS_CHALLENGE.status":"success",
                "JS_CHALLENGE.sessionId":sessionId,
                "IS_WEBGL":True,
                "WEBGLVENDORANDRENDERER":self.device["wr"],
                "IS_WEBGL2":True,
                "WEBGL2VENDORANDRENDERER":self.device["wr"],
                "HASLIEDLANGUAGES":False,
                "HASLIEDRESOLUTION":False,
                "HASLIEDOS":False,
                "HASLIEDBROWSER":False,
                "COLORDEPTH":30,
                "DEVICEMEMORY":8,
                "RESOLUTION":str(self.device["screen"]["width"]) + "," + str(self.device["screen"]["height"]),
                "AVAILABLE_RESOLUTION":str(self.device["screen"]["availWidth"]) + "," + str(self.device["screen"]["availHeight"]),
                "HARDWARECONCURRENCY":10,
                "TIMEZONEOFFSET":-60,
                "TIMEZONE":"Europe/Berlin",
                "SESSIONSTORAGE":True,
                "LOCALSTORAGE":True,
                "INDEXEDDB":True,
                "OPENDATABASE":True,
                "PLATFORM":"MacIntel",
                "IS_CANVAS":True,
                "TOUCH_SUPPORT.maxTouchPoints":0,
                "TOUCH_SUPPORT.touchEvent":False,
                "TOUCH_SUPPORT.touchStart":False,
                "JS_FONTS":4,
                "AUDIO_FINGERPRINT":124.04344968475198,
                "PRODUCT_SUB":self.device["navigator"]["productSub"],
                "EMPTY_EVAL_LENGTH":33,
                "ERRORFF":False,
                "CHROME":True,
                "COOKIES_ENABLED":True,
                "IS_INCOGNITO":False,
                "IS_PRIVATE_MODE":False,
                "IS_WEB_GLSTATUS":-1,
                "HEADLESS.selenium":"",
                "HEADLESS.phantomjs._phantom":"",
                "HEADLESS.phantomjs.__phantomas":"",
                "HEADLESS.phantomjs.callPhantom":"",
                "HEADLESS.nodejs.Buffer":"",
                "HEADLESS.couchjs.emit":"",
                "HEADLESS.rhino.spawn":"",
                "HEADLESS.chromium.domAutomationController":"",
                "HEADLESS.chromium.domAutomation":"",
                "HEADLESS.outerWidth":self.device["window"]["outerWidth"],
                "HEADLESS.outerHeight":self.device["window"]["outerHeight"],
                "HEADLESS.headless_chrome":False,
                "HEADLESS.navigator.webdriver_present":True,
                "HEADLESS.window.chrome_missing":False,
                "HEADLESS.permissions_api_overriden":False,
                "HEADLESS.navigator.plugins_empty":False,
                "HEADLESS.navigator.languages_blank":False,
                "HEADLESS.consistent_plugins_prototype":True,
                "HEADLESS.consistent_mimetypes_prototype":True,
                "HEADLESS.permissions_api":False,
                "HEADLESS.iframe_window.headless_chrome":False,
                "HEADLESS.iframe_window.navigator.webdriver_present":True,
                "HEADLESS.iframe_window.window.chrome_missing":False,
                "HEADLESS.iframe_window.permissions_api_overriden":False,
                "HEADLESS.iframe_window.navigator.plugins_empty":False,
                "HEADLESS.iframe_window.navigator.languages_blank":False,
                "HEADLESS.iframe_window.consistent_plugins_prototype":True,
                "HEADLESS.iframe_window.consistent_mimetypes_prototype":True,
                "HEADLESS.iframe_window.permissions_api":False,
                "STEALTH.srcdoc_throws_error":False,
                "STEALTH.srcdoc_triggers_window_proxy":False,
                "STEALTH.index_chrome_too_high":False,
                "STEALTH.chrome_runtime_functions_invalid":False,
                "STEALTH.Function_prototype_toString_invalid_typeError":True,
                "REF_LINK":"",
                "PLUGINS.length":5,
                "PLUGINS.details.0.length":2,
                "PLUGINS.details.0.name":"PDF Viewer",
                "PLUGINS.details.0.filename":"internal-pdf-viewer",
                "PLUGINS.details.1.length":2,
                "PLUGINS.details.1.name":"Chrome PDF Viewer",
                "PLUGINS.details.1.filename":"internal-pdf-viewer",
                "PLUGINS.details.2.length":2,
                "PLUGINS.details.2.name":"Chromium PDF Viewer",
                "PLUGINS.details.2.filename":"internal-pdf-viewer",
                "PLUGINS.details.3.length":2,
                "PLUGINS.details.3.name":"Microsoft Edge PDF Viewer",
                "PLUGINS.details.3.filename":"internal-pdf-viewer",
                "PLUGINS.details.4.length":2,
                "PLUGINS.details.4.name":"WebKit built-in PDF",
                "PLUGINS.details.4.filename":"internal-pdf-viewer",
                "AUDIO":2,
                "VIDEO":1,
                "VIDEO_INPUT_DEVICES":"",
                "AUDIO_INPUT_DEVICES":"",
                "AUDIO_OUTPUT_DEVICES":"",
                "MEDIA_CODEC_MP4_AVC1":"probably",
                "MEDIA_CODEC_X_M4A":"maybe",
                "MEDIA_CODEC_AAC":"probably",
                "MEMORY_HEAP_SIZE_LIMIT":4294705152,
                "MEMORY_TOTAL_HEAP_SIZE":25017985,
                "MEMORY_USED_HEAP_SIZE":12371629,
                "IS_ACCEPT_COOKIES":True,
                "selenium_in_document":False,
                "selenium_in_window":False,
                "selenium_in_navigator":False,
                "selenium_sequentum":False,
                "DOCUMENT_ELEMENT_SELENIUM":"",
                "DOCUMENT_ELEMENT_WEBDRIVER":"",
                "DOCUMENT_ELEMENT_DRIVER":"",
                "window_html_webdriver":False,
                "window_geb":False,
                "window_awesomium":False,
                "window_RunPerfTest":False,
                "window_fmget_targets":False,
                "hasTrustToken":False,
                "trustTokenOperationError":False,
                "setTrustToken":False,
                "trustToken":False,
                "localStorage.length":7,
                "sessionStorage.length":11,
                "WEB_RTC_ENABLED":True,
                "MQ_SCREEN.matches":True,
                "MQ_SCREEN.media":"(min-width: 1288px)",
                "IFRAME_CHROME":"object",
                "IFRAME_WIDTH":self.device["screen"]["width"],
                "IFRAME_HEIGHT":self.device["screen"]["height"],
                "NOTIFICATION_PERMISSION":"default",
                "HAS_CHROME_APP":True,
                "HAS_CHROME_CSI":True,
                "HAS_CHROME_LOADTIMES":True,
                "HAS_CHROME_RUNTIME":False,
                "CHROMIUM_MATH":True,
                "CHROME_PROPERTY_DESCRIPTOR_APP":"""{\\"configurable\\":true,\\"enumerable\\":true,\\"value\\":{\\"isInstalled\\":false,\\"InstallState\\":{\\"DISABLED\\":\\"disabled\\",\\"INSTALLED\\":\\"installed\\",\\"NOT_INSTALLED\\":\\"not_installed\\"},\\"RunningState\\":{\\"CANNOT_RUN\\":\\"cannot_run\\",\\"READY_TO_RUN\\":\\"ready_to_run\\",\\"RUNNING\\":\\"running\\"}},\\"writable\\":True}","CHROME_PROPERTY_DESCRIPTOR_CSI":"{\\"configurable\\":true,\\"enumerable\\":true,\\"writable\\":true}","CHROME_PROPERTY_DESCRIPTOR_LOADTIMES":"undefined","CHROME_PROPERTY_DESCRIPTOR_RUNTIME":"undefined","NAVIGATOR_PROPERTY_DESCRIPTOR_LANGUAGES":"{\\"configurable\\":true,\\"enumerable\\":true,\\"getter\\":\\"function get languages() { [native code] }\\"}""",
                "NAVIGATOR_PROPERTY_DESCRIPTOR_HARDWARECONCURRENCY":"""{\\"configurable\\":true,\\"enumerable\\":true,\\"getter\\":\\"function get hardwareConcurrency() { [native code] }\\"}","SCREEN_PROPERTY_DESCRIPTOR_WIDTH":"{\\"configurable\\":true,\\"enumerable\\":true,\\"getter\\":\\"function get width() { [native code] }\\"}""",
                "SCREEN_PROPERTY_DESCRIPTOR_HEIGHT":"""{\\"configurable\\":true,\\"enumerable\\":true,\\"getter\\":\\"function get height() { [native code] }\\"}""",
                "NAVIGATOR_PROPERTY_DESCRIPTOR_WEBDRIVER":"undefined",
                "WINDOW_PROPERTY_DESCRIPTOR_OUTERWIDTH":"""{\\"configurable\\":true,\\"enumerable\\":true,\\"getter\\":\\"function get outerWidth() { [native code] }\\"}""",
                "WINDOW_PROPERTY_DESCRIPTOR_OUTERHEIGHT":"""{\\"configurable\\":true,\\"enumerable\\":true,\\"getter\\":\\"function get outerHeight() { [native code] }\\"}"""
            },
            "ioMetadata":{
                "BLUTOOTH_SUPPORTED":True,
                "HAS_SPEAKERS":True,
                "HAS_MICROPHONE":True,
                "HAS_CAMERA":True,
                "BATTERY_SUPPORTED":True,
                "BATTERY_LEVEL":round(random.random(),2),
                "BATTERY_CHARGING":False,
                "BATTERY_CHARGING_TIME":None,
                "BATTERY_DISCHARGING_TIME":random.randint(10000,30000),
                "GPS_SUPPORTED":True,
                "IS_MOBILE":False,
                "HAS_TOUCH":False,
                "PERMISSIONS.accelerometer":"granted",
                "PERMISSIONS.background-sync":"granted",
                "PERMISSIONS.camera":"prompt",
                "PERMISSIONS.clipboard-read":"prompt",
                "PERMISSIONS.clipboard-write":"granted",
                "PERMISSIONS.geolocation":"prompt",
                "PERMISSIONS.gyroscope":"granted",
                "PERMISSIONS.magnetometer":"granted",
                "PERMISSIONS.microphone":"prompt",
                "PERMISSIONS.midi":"granted",
                "PERMISSIONS.notifications":"prompt",
                "PERMISSIONS.payment-handler":"granted",
                "PERMISSIONS.persistent-storage":"prompt",
                "PREFERS_COLOR_SCHEME":"light"
            },
            "baseTimestamp":round(time.time() * 1000),
            "epochTimeInMillis":round(time.time() * 1000)
        }

        compressed_data = gzip.compress(json.dumps(post_data).encode("utf-8"))
        encrypted_data = self.encrypt(compressed_data)
        return encrypted_data
    
    @staticmethod
    def encrypt(data):
        """Encrypts data using the static key
        
        Args:
            data (bytes): Data to encrypt
        
        Returns:
            bytes: Encrypted data
        """
        a = bytearray(len(data))
        for i in range(len(data)):
            a[i] = data[i] ^ ord(SecuredTouch.T[i % len(SecuredTouch.T)])
        return bytes(a)
    
    @staticmethod
    def decrypt(data):
        """Decrypts data using the static key

        Args:
            data (bytes): Data to decrypt
        
        Returns:
            bytes: Decrypted data
        """
        a = bytearray(len(data))
        for i in range(len(data)):
            a[i] = data[i] ^ ord(SecuredTouch.T[i % len(SecuredTouch.T)])
        return gzip.decompress(bytes(a))

    @staticmethod
    def get_chrome_version(user_agent : str):
        """Gets the chrome version from the user agent

        Args:
            user_agent (str): User agent used in requests

        Returns:
            str: Chrome version
        """
        if "Chrome" in user_agent:
            return user_agent.split("Chrome/")[1].split(" ")[0]
        else:
            raise Unsupported_UserAgent_Exception("User agent is not Chrome!")
    
    @staticmethod
    def get_os_version(user_agent : str):
        """Gets the OS version from the user agent (Windows, Mac)
        
        Args:
            user_agent (str): User agent used in requests
        
        Returns:
            str: OS version
        """
        if "Windows" in user_agent:
            return user_agent.split("Windows NT ")[1].split(";")[0]
        elif "Macintosh" in user_agent:
            return user_agent.split("Mac OS X ")[1].split(")")[0].replace("_", ".")
        else:
            raise Unsupported_UserAgent_Exception("User Agent not supported! We only support Windows and Mac OS X user agents.")
    
    @staticmethod
    def get_platform(user_agent : str):
        """Gets the platform from the user agent
        
        Args:
            user_agent (str): User agent used in requests
        
        Returns:
            str: Platform
        """
        if "Mac OS" in user_agent:
            return "Mac OS"
        elif "Windows" in user_agent:
            return "Windows"
        else:
            return Unsupported_UserAgent_Exception("User Agent not supported! We only support Windows and Mac OS X user agents.")
    
    @staticmethod
    def get_device_type(user_agent : str):
        """Gets the device type from the user agent
        
        Args:
            user_agent (str): User agent used in requests
        
        Returns:
            str: Device type
        """
        return f"Chrome({SecuredTouch.get_chrome_version(user_agent)})-{SecuredTouch.get_platform(user_agent)}({SecuredTouch.get_os_version(user_agent)})"
    
    @staticmethod
    def getDevice():
        """Gets a random device from json file
        
        Returns:
            dict: Device
        """
        with open(PATH) as devices_file:
            devices = json.load(devices_file)
            return random.choice(devices)