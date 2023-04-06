from datetime import datetime
from os import urandom
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
import pytz
import json
import base64
import math
import hashlib
import ctypes
import requests
import re
import base64
import random


class Encryptor:
    def __init__(self, adyen_public_key, adyen_version='_0_1_8', adyen_prefix='adyenjs'):
        """
        :param adyen_public_key: adyen key, looks like this: "10001|A2370..."
        :param adyen_version: version of adyen encryption, looks like this: _0_1_8
        :param adyen_prefix: prefix before adyen version. can vary depending on where you are submitting the payment. typically is just "adyenjs"
        """

        self.adyen_public_key = adyen_public_key
        self.adyen_version = adyen_version
        self.adyen_prefix = adyen_prefix

    def encrypt_field(self, name: str, value: str):
        """
        :param name: name of field you want to encrypt, for ex, "cvc"
        :param value: value of the field you want to encrypt
        :return: a string containing the adyen-encrypted field
        """

        plain_card_data = self.field_data(name, value)
        card_data_json_string = json.dumps(plain_card_data, sort_keys=True)

        # Encrypt the actual card data with symmetric encryption
        aes_key = self.generate_aes_key()
        nonce = self.generate_nonce()
        encrypted_card_data = self.encrypt_with_aes_key(aes_key, nonce, bytes(card_data_json_string, encoding='utf-8'))
        encrypted_card_component = nonce + encrypted_card_data

        # Encrypt the AES Key with asymmetric encryption
        public_key = self.decode_adyen_public_key(self.adyen_public_key)
        encrypted_aes_key = self.encrypt_with_public_key(public_key, aes_key)

        return "{}{}${}${}".format(self.adyen_prefix,
                                   self.adyen_version,
                                   base64.standard_b64encode(encrypted_aes_key).decode(),
                                   base64.standard_b64encode(encrypted_card_component).decode())

    def encrypt_card(self, card: str, cvv: str, month: str, year: str):
        """
        :param card: card number string
        :param cvv: cvv number string
        :param month: card month string
        :param year: card year string
        :return: dictionary with all encrypted card fields (card, cvv, month, year)
        """

        data = {
            'card': self.encrypt_field('number', card),
            'cvv': self.encrypt_field('cvc', cvv),
            'month': self.encrypt_field('expiryMonth', month),
            'year': self.encrypt_field('expiryYear', year),
        }

        return data

    def field_data(self, name, value):
        """
        :param name: name of field
        :param value: value of field
        :return: a dict to be encrypted
        """

        generation_time = datetime.now(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        field_data_json = {
            name: value,
            "generationtime": generation_time
        }

        return field_data_json

    def encrypt_from_dict(self, dict_: dict):
        plain_card_data = dict_
        card_data_json_string = json.dumps(plain_card_data, sort_keys=True)

        # Encrypt the actual card data with symmetric encryption
        aes_key = self.generate_aes_key()
        nonce = self.generate_nonce()
        encrypted_card_data = self.encrypt_with_aes_key(aes_key, nonce, bytes(card_data_json_string, encoding='utf-8'))
        encrypted_card_component = nonce + encrypted_card_data

        # Encrypt the AES Key with asymmetric encryption
        public_key = self.decode_adyen_public_key(self.adyen_public_key)
        encrypted_aes_key = self.encrypt_with_public_key(public_key, aes_key)

        return "{}{}${}${}".format(self.adyen_prefix,
                                   self.adyen_version,
                                   base64.standard_b64encode(encrypted_aes_key).decode(),
                                   base64.standard_b64encode(encrypted_card_component).decode())

    @staticmethod
    def decode_adyen_public_key(encoded_public_key):
        backend = default_backend()
        key_components = encoded_public_key.split("|")
        public_number = rsa.RSAPublicNumbers(int(key_components[0], 16), int(key_components[1], 16))
        return backend.load_rsa_public_numbers(public_number)

    @staticmethod
    def encrypt_with_public_key(public_key, plaintext):
        ciphertext = public_key.encrypt(plaintext, padding.PKCS1v15())
        return ciphertext

    @staticmethod
    def generate_aes_key():
        return AESCCM.generate_key(256)

    @staticmethod
    def encrypt_with_aes_key(aes_key, nonce, plaintext):
        cipher = AESCCM(aes_key, tag_length=8)
        ciphertext = cipher.encrypt(nonce, plaintext, None)
        return ciphertext

    @staticmethod
    def generate_nonce():
        return urandom(12)

class Fingerprint():
    def __init__(self, device):
        # Default
        self.plugins = 10
        self.nrOfPlugins = 3
        self.fonts = 10
        self.nrOfFonts = 3
        self.timeZone = 10
        self.video = 10
        self.superCookies = 10
        self.userAgent = 10
        self.mimeTypes = 10
        self.nrOfMimeTypes = 3
        self.canvas = 10
        self.cpuClass = 5
        self.platform = 5
        self.doNotTrack = 5
        self.webglFp = 10
        self.jsFonts = 10

        # Artificial
        self.userAgentString = device['navigator']['userAgent']

        self.pluginsString = "Plugin 0: Chrome PDF Viewer; Portable Document Format; internal-pdf-viewer; (Portable Document Format; application/pdf; pdf) (Portable Document Format; text/pdf; pdf). Plugin 1: Chromium PDF Viewer; Portable Document Format; internal-pdf-viewer; (Portable Document Format; application/pdf; pdf) (Portable Document Format; text/pdf; pdf). Plugin 2: Microsoft Edge PDF Viewer; Portable Document Format; internal-pdf-viewer; (Portable Document Format; application/pdf; pdf) (Portable Document Format; text/pdf; pdf). Plugin 3: PDF Viewer; Portable Document Format; internal-pdf-viewer; (Portable Document Format; application/pdf; pdf) (Portable Document Format; text/pdf; pdf). Plugin 4: WebKit built-in PDF; Portable Document Format; internal-pdf-viewer; (Portable Document Format; application/pdf; pdf) (Portable Document Format; text/pdf; pdf). "
        self.pluginCount = 5

        self.screenWidth = device['screen']['width']
        self.screenHeight = device['screen']['height']
        self.screenColorDepth = device['screen']['colorDepth']

        self.deviceStorage = 'DOM-LS: Yes, DOM-SS: Yes'
        self.oXMLStorage = ', IE-UD: No'

        self.mimeTypesString = "Portable Document Formatapplication/pdfpdfPortable Document Formattext/pdfpdf"
        self.mimeTypesLength = 2

        self.platformString = device['navigator']['platform']

        self.doNotTrackString = "1"

        self.entropy = "40"

    def getSuperCookies(self):
        superCookiesPadding = math.floor(self.superCookies / 2)

        deviceStorageValue = self.calculate_md5(self.deviceStorage, superCookiesPadding)
        IEUDValue = self.calculate_md5(self.oXMLStorage, superCookiesPadding)

        superCookies = deviceStorageValue + IEUDValue
        return superCookies

    def getEntropy(self):
        mobile = ["iPad", "iPhone", "iPod"]
        if self.userAgent in mobile:
            return "20"
        return "40"

    def padString(self, string, num):
        paddedString = string.rjust(num, "0")
        if len(paddedString) > num:
            return paddedString[0:num]
        return paddedString

    def calculate_md5(self, string, num):
        a = hashlib.md5(string.encode())
        hashed_string = base64.b64encode(a.digest()).decode()
        return_string = self.padString(hashed_string, num)
        return return_string

    def generateFingerprint(self):
        self.plugins = self.calculate_md5(self.pluginsString, self.plugins)
        self.nrOfPlugins = self.padString(str(self.pluginCount), self.nrOfPlugins)
        self.fonts = self.padString("", self.fonts)
        self.nrOfFonts = self.padString("", self.nrOfFonts)
        self.timeZone = "CK1aUgqatB"
        self.video = self.padString(str((self.screenWidth + 7) * (self.screenHeight + 7) * self.screenColorDepth),
                                    self.video)
        self.superCookies = self.getSuperCookies()
        self.userAgent = self.calculate_md5(self.userAgentString, self.userAgent)
        self.mimeTypes = self.calculate_md5(self.mimeTypesString, self.mimeTypes)
        self.nrOfMimeTypes = self.padString(str(self.mimeTypesLength), self.nrOfMimeTypes)
        self.canvas = "rKkEK1Ha8P"
        self.cpuClass = self.padString("", self.cpuClass)
        self.platform = self.calculate_md5(self.platformString, self.platform)
        self.doNotTrack = self.calculate_md5(self.doNotTrackString, self.doNotTrack)
        self.jsFonts = "iZCqnI4lsk"
        self.webglFp = "fKkhnraRhX"
        self.entropy = self.getEntropy()

        adyenFingerprint = f"{self.plugins}{self.nrOfPlugins}{self.fonts}{self.nrOfFonts}{self.timeZone}{self.video}{self.superCookies}{self.userAgent}{self.mimeTypes}{self.nrOfMimeTypes}{self.canvas}{self.cpuClass}{self.platform}{self.doNotTrack}{self.webglFp}{self.jsFonts}:{self.entropy}".replace(
            "+", "G").replace("/", "D")
        """
        c = a.plugins + 
        a.nrOfPlugins + 
        a.fonts + 
        a.nrOfFonts + 
        a.timeZone + 
        a.video + 
        a.superCookies + 
        a.userAgent + 
        a.mimeTypes + 
        a.nrOfMimeTypes + 
        a.canvas + 
        a.cpuClass + 
        a.platform + 
        a.doNotTrack + 
        a.webglFp + 
        a.jsFonts;

        print("Plugins:", self.plugins)
        print("Plugins NR:", self.nrOfPlugins)
        print("Fonts:", self.fonts)
        print("Fonts NR:", self.nrOfFonts)
        print("timeZone:", self.timeZone)
        print("Video:", self.video)
        print("Super Cookies:", self.superCookies)
        print("User Agent:", self.userAgent)
        print("Mime Types:", self.mimeTypes)
        print("Mime Types NR:", self.nrOfMimeTypes)
        print("Canvas:", self.canvas)
        print("CPU Class:", self.cpuClass)
        print("Platform:", self.platform)
        print("doNotTrack:", self.doNotTrack)
        print("WebGLFp:", self.webglFp)
        print("jsFonts:", self.jsFonts)
        print("Entropy:", self.entropy)

        print("Adyen Fingerprint:", adyenFingerprint)
         """
        return adyenFingerprint


##################################
# Title  :  DeviceId (FTL)       #
# Author :  Bwonderkid#2121      #
# Created:  08.12.2022           #

# Updated:  12.12.2022           #
# By     :  Bwonderkid#2121      #
# Changes:                       #
#       - Finished Generation    #
##################################

class DeviceID():
    def __init__(self, session:requests.Session, location:str, referrer:str, scripturl:str):
        """
        Initialize the DeviceID class

        Args:
            session (requests.Session): The session to use
            location (str): Current Browser location url
            referrer (str): Last Browser referrer url
            scripturl (str): The url to the script
        """

        self.getScript(session,location,scripturl)
        self.apname = "Netscape"
        self.apver = session.headers["user-agent"].split("Mozilla/")[-1]

        if "Windows" in self.apver:
            self.jbros = self.apver.split("(")[-1].split(";")[0]
        else:
            self.jbros = self.apver.split("; ")[-1].split(")")[0]

        if "windows" in self.apver.lower():
            self.nplat = "Win32"
        elif "macintosh" in self.apver.lower():
            self.nplat = "MacIntel"
        elif "linux" in self.apver.lower():
            self.nplat = "Linux x86_64"
        else:
            raise Exception("User Agent not supported")

        if "Chrome" in self.apver:
            self.jbrnm = "Chrome"
            self.jbrvr = self.apver.split("Chrome/")[-1].split(" ")[0]
        elif "Safari" in self.apver:
            self.jbrnm = "Safari"
            self.jbrvr = self.apver.split("Safari/")[-1].split(" ")[0]
        else:
            raise Exception("User Agent not supported")


        self.data = {
            "INTLOC": location,
            "JINT": "form",
            "JENBL": "1",
            "JSSRC": self.jssrc,
            "UAGT": session.headers["user-agent"],
            "JSTOKEN": self.jstoken,
            "HACCLNG": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "JSVER": self.jsver,
            "TZON": "-60",
            "JSTIME": self.svrtime,
            "SVRTIME": self.svrtime,
            "JBRNM": self.jbrnm,
            "JBRVR": self.jbrvr,
            "JBROS": self.jbros,
            "APVER": self.apver,
            "APNAM": self.apname,
            "NPLAT": self.nplat,
            "JBRCM": "KHTML, like Gecko",
            "JLANG": "de",
            "IGGY": self.iggy,
            "JRES": f"{random.randint(1000,3000)}x{random.randint(1000,3000)}",
            "JPLGNS": "internal-pdf-viewer;internal-pdf-viewer;internal-pdf-viewer;internal-pdf-viewer;internal-pdf-viewer;",
            "JREFRR": referrer,
            "LSTOKEN": self.jstoken,
            "CTOKEN": self.jstoken,
            "WDBTOKEN": self.jstoken,
        }

        if "s3.global-e.com" in scripturl:
            insert = lambda _dict, obj, pos: {k: v for k, v in (list(_dict.items())[:pos] + list(obj.items()) + list(_dict.items())[pos:])}

            self.data = insert(self.data, {"FLRTD":self.flrtd}, 0)
            self.data = insert(self.data, {"JDIFF":"1"}, 5)
            self.data =insert(self.data, {"SUAGT":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"}, 6)
            self.data["HACCLNG"] = "en-IL,en-US;q=0.8,en;q=0.5,he;q=0.3"
            self.data = insert(self.data, {"BBOUT":"aioBlackBox"}, 16)
            self.data = insert(self.data, {"WDBERROR":"SecurityError: Failed to execute 'openDatabase' on 'Window': Access to the WebDatabase API is denied in third party contexts."}, -1)
            self.data.pop("JSTOKEN",None)
            self.data.pop("LSTOKEN",None)
            self.data.pop("CTOKEN",None)
            self.data.pop("WDBTOKEN",None)


    
    def getScript(self, session:requests.Session, referer:str, scripturl:str):
        """
        Get the deviceId script
        
        Args:
            session (requests.Session): The session to use
            
        Raises:
            Exception: Failed to get deviceId script
        """

        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de,de-DE;q=0.9,en-US;q=0.8,en;q=0.7",
            "referer": "https://" + referer.split("//")[1].split("/")[0] + "/",
            "sec-fetch-dest": "script",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "cross-site",
            "user-agent": session.headers["user-agent"],
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        for _ in range(5):
            res = session.get(scripturl, headers=headers) # https://mpsnare.iesnare.com/snare.js, https://s3.global-e.com/snare.js
            if res:
                self.script = res.text
                self.flrtd = re.findall(r'"FLRTD","(.*?)"', self.script)[0]
                self.jstoken = re.findall(r'"JSTOKEN","(.*?)"', self.script)[0]
                self.jssrc = base64.b64decode(re.findall(r'"JSSRC",_i_o.__if_ap\("(.*?)"\)', self.script)[0].encode()).decode()
                self.iggy = re.findall(r'"IGGY","(.*?)"', self.script)[0]
                self.jsver = re.findall(r'"JSVER","(.*?)"', self.script)[0]
                self.svrtime = re.findall(r'"SVRTIME","(.*?)"', self.script)[0]
                break
        else:
            raise Exception("Failed to get deviceId script")
    
    def toString(self):
        """
        Convert the data to a string
        
        Returns:
            str: The object data as a string
        """

        _i_cs = 0
        _i_al = ""
        for _i_ct in self.data:
            _i_cs += 1
            _i_al += f"{DeviceID._if_q(len(_i_ct), 4)}{_i_ct.upper()}{DeviceID._if_q(len(self.data[_i_ct]), 4)}{self.data[_i_ct]}"
        return DeviceID._if_q(_i_cs, 4) + _i_al

    def generate(self): # _if_cz
        """
        Generate the deviceId
        
        Returns:
            str: The deviceId
        """

        _i_cv = self._if_bv(self.toString())
        return "0400" + DeviceID._if_ai(_i_cv)
    
    def _if_ai(_i_al):
        """
        Encode the data
        
        Args:
            _i_al (str): The data to encode
        
        Returns:
            str: The encoded data
        """

        _i_ft = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        _i_e = ""
        _i_g = 0
        while _i_g < len(_i_al):
            try:
                _i_p = ctypes.c_int(ord(_i_al[_i_g])).value
            except Exception:
                exception_p = True
                _i_p = 0
            try:
                _i_q = ctypes.c_int(ord(_i_al[_i_g+1])).value
            except Exception:
                exception_q = True
                _i_q = 0
            try:
                _i_r = ctypes.c_int(ord(_i_al[_i_g+2])).value
            except Exception:
                exception_r = True
                _i_r = 0
            _i_s = _i_p >> 2
            _i_t = ((_i_p & 3) << 4) | (_i_q >> 4)
            _i_u = ((_i_q & 15) << 2) | (_i_r >> 6)
            _i_v = _i_r & 63
            if _i_q == 0 and exception_q:
                _i_u = 64
                _i_v = 64
            elif _i_r == 0 and exception_r:
                _i_v = 64
            _i_e += _i_ft[_i_s] + _i_ft[_i_t] + _i_ft[_i_u] + _i_ft[_i_v]
            _i_g += 3
            exception_q = exception_r = False
        return _i_e
            
    @staticmethod
    def _if_bv(_if_gp): # __if_hb
        """
        Encrypt the data
        
        Args:
            _if_gp (str): The data to encrypt
        
        Returns:
            str: The encrypted data
        """

        _i_az = [16843776, 0, 65536, 16843780, 16842756, 66564, 4, 65536, 1024, 16843776, 16843780, 1024, 16778244, 16842756, 16777216, 4, 1028, 16778240, 16778240, 66560, 66560, 16842752, 16842752, 16778244, 65540, 16777220, 16777220, 65540, 0, 1028, 66564, 16777216, 65536, 16843780, 4, 16842752, 16843776, 16777216, 16777216, 1024, 16842756, 65536, 66560, 16777220, 1024, 4, 16778244, 66564, 16843780, 65540, 16842752, 16778244, 16777220, 1028, 66564, 16843776, 1028, 16778240, 16778240, 0, 65540, 66560, 0, 16842756]
        _i_ba = [-2146402272, -2147450880, 32768, 1081376, 1048576, 32, -2146435040, -2147450848, -2147483616, -2146402272, -2146402304, -2147483648, -2147450880, 1048576, 32, -2146435040, 1081344, 1048608, -2147450848, 0, -2147483648, 32768, 1081376, -2146435072, 1048608, -2147483616, 0, 1081344, 32800, -2146402304, -2146435072, 32800, 0, 1081376, -2146435040, 1048576, -2147450848, -2146435072, -2146402304, 32768, -2146435072, -2147450880, 32, -2146402272, 1081376, 32, 32768, -2147483648, 32800, -2146402304, 1048576, -2147483616, 1048608, -2147450848, -2147483616, 1048608, 1081344, 0, -2147450880, 32800, -2147483648, -2146435040, -2146402272, 1081344]
        _i_bb = [520, 134349312, 0, 134348808, 134218240, 0, 131592, 134218240, 131080, 134217736, 134217736, 131072, 134349320, 131080, 134348800, 520, 134217728, 8, 134349312, 512, 131584, 134348800, 134348808, 131592, 134218248, 131584, 131072, 134218248, 8, 134349320, 512, 134217728, 134349312, 134217728, 131080, 520, 131072, 134349312, 134218240, 0, 512, 131080, 134349320, 134218240, 134217736, 512, 0, 134348808, 134218248, 131072, 134217728, 134349320, 8, 131592, 131584, 134217736, 134348800, 134218248, 520, 134348800, 131592, 8, 134348808, 131584]
        _i_bc = [8396801, 8321, 8321, 128, 8396928, 8388737, 8388609, 8193, 0, 8396800, 8396800, 8396929, 129, 0, 8388736, 8388609, 1, 8192, 8388608, 8396801, 128, 8388608, 8193, 8320, 8388737, 1, 8320, 8388736, 8192, 8396928, 8396929, 129, 8388736, 8388609, 8396800, 8396929, 129, 0, 0, 8396800, 8320, 8388736, 8388737, 1, 8396801, 8321, 8321, 128, 8396929, 129, 1, 8192, 8388609, 8193, 8396928, 8388737, 8193, 8320, 8388608, 8396801, 128, 8388608, 8192, 8396928]
        _i_bd = [256, 34078976, 34078720, 1107296512, 524288, 256, 1073741824, 34078720, 1074266368, 524288, 33554688, 1074266368, 1107296512, 1107820544, 524544, 1073741824, 33554432, 1074266112, 1074266112, 0, 1073742080, 1107820800, 1107820800, 33554688, 1107820544, 1073742080, 0, 1107296256, 34078976, 33554432, 1107296256, 524544, 524288, 1107296512, 256, 33554432, 1073741824, 34078720, 1107296512, 1074266368, 33554688, 1073741824, 1107820544, 34078976, 1074266368, 256, 33554432, 1107820544, 1107820800, 524544, 1107296256, 1107820800, 34078720, 0, 1074266112, 1107296256, 524544, 33554688, 1073742080, 524288, 0, 1074266112, 34078976, 1073742080]
        _i_be = [536870928, 541065216, 16384, 541081616, 541065216, 16, 541081616, 4194304, 536887296, 4210704, 4194304, 536870928, 4194320, 536887296, 536870912, 16400, 0, 4194320, 536887312, 16384, 4210688, 536887312, 16, 541065232, 541065232, 0, 4210704, 541081600, 16400, 4210688, 541081600, 536870912, 536887296, 16, 541065232, 4210688, 541081616, 4194304, 16400, 536870928, 4194304, 536887296, 536870912, 16400, 536870928, 541081616, 4210688, 541065216, 4210704, 541081600, 0, 541065232, 16, 16384, 541065216, 4210704, 16384, 4194320, 536887312, 0, 541081600, 536870912, 4194320, 536887312]
        _i_bf = [2097152, 69206018, 67110914, 0, 2048, 67110914, 2099202, 69208064, 69208066, 2097152, 0, 67108866, 2, 67108864, 69206018, 2050, 67110912, 2099202, 2097154, 67110912, 67108866, 69206016, 69208064, 2097154, 69206016, 2048, 2050, 69208066, 2099200, 2, 67108864, 2099200, 67108864, 2099200, 2097152, 67110914, 67110914, 69206018, 69206018, 2, 2097154, 67108864, 67110912, 2097152, 69208064, 2050, 2099202, 69208064, 2050, 67108866, 69208066, 69206016, 2099200, 0, 2, 69208066, 0, 2099202, 69206016, 2048, 67108866, 67110912, 2048, 2097154]
        _i_bg = [268439616, 4096, 262144, 268701760, 268435456, 268439616, 64, 268435456, 262208, 268697600, 268701760, 266240, 268701696, 266304, 4096, 64, 268697600, 268435520, 268439552, 4160, 266240, 262208, 268697664, 268701696, 4160, 0, 0, 268697664, 268435520, 268439552, 266304, 262144, 266304, 262144, 268701696, 4096, 64, 268697664, 4096, 266304, 268439552, 64, 268435520, 268697600, 268697664, 268435456, 262144, 268439616, 0, 268701760, 262208, 268435520, 268697600, 268439552, 268439616, 0, 268701760, 266240, 266240, 4160, 4160, 262208, 268435456, 268701696]
        _i_bh = [404892696, 707799300, 420098074, 537469232, 86380816, 134943501, 83893292, 740623361, 103876868, 856114, 353698365, 554967570, 805385473, 286198314, 1025582131, 100795396, 403244054, 589311268, 840568850, 2752779, 50338305, 254948609, 570959884, 338757657, 236194566, 303040022, 135136289, 288623378, 706946563, 402657825, 153421875, 906500132] #_if_cj(__if_hb)
        _i_bi = 0
        _i_bj = len(_if_gp)
        _i_bk = 0
        _i_br = [0, 32, 2]
        _i_by = 3
        _if_gp += ""
        _i_e = ""
        _i_bz = ""
        while _i_bi < _i_bj:
            try:
                _i_bp_1 = ctypes.c_int(ord(_if_gp[_i_bi]) << 24).value 
            except Exception:
                _i_bp_1 = 0
            _i_bi += 1
            try:
                _i_bp_2 = ctypes.c_int(ord(_if_gp[_i_bi]) << 16).value
            except Exception:
                _i_bp_2 = 0
            _i_bi += 1
            try:
                _i_bp_3 = ctypes.c_int(ord(_if_gp[_i_bi]) << 8).value 
            except Exception:
                _i_bp_3 = 0
            _i_bi += 1
            try:
                _i_bp_4 = ctypes.c_int(ord(_if_gp[_i_bi])).value
            except Exception:
                _i_bp_4 = 0
            _i_bi += 1
            _i_bp = _i_bp_1 ^ _i_bp_2 ^ _i_bp_3 ^ _i_bp_4
            try:
                _i_bq_1 = ctypes.c_int(ord(_if_gp[_i_bi]) << 24).value
            except Exception:
                _i_bq_1 = 0
            _i_bi += 1
            try:
                _i_bq_2 = ctypes.c_int(ord(_if_gp[_i_bi]) << 16).value
            except Exception:
                _i_bq_2 = 0
            _i_bi += 1
            try:
                _i_bq_3 = ctypes.c_int(ord(_if_gp[_i_bi]) << 8).value
            except Exception:
                _i_bq_3 = 0
            _i_bi += 1
            try:
                _i_bq_4 = ord(_if_gp[_i_bi])
            except Exception:
                _i_bq_4 = 0
            _i_bi += 1
            _i_bq = _i_bq_1 ^ _i_bq_2 ^ _i_bq_3 ^ _i_bq_4
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bp,4) ^ _i_bq) & 252645135
            _i_bq ^= _i_aw
            _i_bp ^= ctypes.c_int(_i_aw << 4).value
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bp, 16) ^ _i_bq) & 65535
            _i_bq ^= _i_aw
            _i_bp ^= ctypes.c_int(_i_aw << 16).value
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bq, 2) ^ _i_bp) & 858993459
            _i_bp ^= _i_aw
            _i_bq ^= ctypes.c_int(_i_aw << 2).value
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bq, 8) ^ _i_bp) & 16711935
            _i_bp ^= _i_aw
            _i_bq ^= ctypes.c_int(_i_aw << 8).value
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bp, 1) ^ _i_bq) & 1431655765
            _i_bq ^= _i_aw
            _i_bp ^= ctypes.c_int(_i_aw << 1).value
            _i_bp = ctypes.c_int(_i_bp << 1).value | DeviceID.zero_fill_right_shift(_i_bp, 31)
            _i_bq = ctypes.c_int(_i_bq << 1).value | DeviceID.zero_fill_right_shift(_i_bq, 31)
            _i_bl = 0
            while _i_bl < _i_by:
                _i_bw = _i_br[_i_bl + 1]
                _i_bx = _i_br[_i_bl + 2]
                _i_g = _i_br[_i_bl]
                while _i_g != _i_bw:
                    _i_bn = _i_bq ^ _i_bh[_i_g]
                    _i_bo = (DeviceID.zero_fill_right_shift(_i_bq, 4) | ctypes.c_int(_i_bq << 28).value) ^ _i_bh[_i_g + 1]
                    _i_aw = _i_bp
                    _i_bp = _i_bq
                    _i_bq = _i_aw ^ (_i_ba[DeviceID.zero_fill_right_shift(_i_bn ,24) & 63] | _i_bc[DeviceID.zero_fill_right_shift(_i_bn ,16) & 63] | _i_be[DeviceID.zero_fill_right_shift(_i_bn ,8) & 63] | _i_bg[_i_bn & 63] | _i_az[DeviceID.zero_fill_right_shift(_i_bo ,24) & 63] | _i_bb[DeviceID.zero_fill_right_shift(_i_bo ,16) & 63] | _i_bd[DeviceID.zero_fill_right_shift(_i_bo ,8) & 63] | _i_bf[_i_bo & 63])
                    _i_g += _i_bx
                _i_aw = _i_bp
                _i_bp = _i_bq
                _i_bq = _i_aw
                _i_bl += 3
            _i_bp = DeviceID.zero_fill_right_shift(_i_bp, 1) | ctypes.c_int(_i_bp << 31).value
            _i_bq = DeviceID.zero_fill_right_shift(_i_bq, 1) | ctypes.c_int(_i_bq << 31).value
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bp, 1) ^ _i_bq) & 1431655765
            _i_bq ^= _i_aw
            _i_bp ^= _i_aw << 1
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bq, 8) ^ _i_bp) & 16711935
            _i_bp ^= _i_aw
            _i_bq ^= _i_aw << 8
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bq, 2) ^ _i_bp) & 858993459
            _i_bp ^= _i_aw
            _i_bq ^= _i_aw << 2
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bp, 16) ^ _i_bq) & 65535
            _i_bq ^= _i_aw
            _i_bp ^= _i_aw << 16
            _i_aw = (DeviceID.zero_fill_right_shift(_i_bp, 4) ^ _i_bq) & 252645135
            _i_bq ^= _i_aw
            _i_bp ^= _i_aw << 4
            _i_bz += DeviceID.fromCharCode(DeviceID.zero_fill_right_shift(_i_bp, 24), DeviceID.zero_fill_right_shift(_i_bp, 16) & 255, DeviceID.zero_fill_right_shift(_i_bp, 8) & 255, _i_bp & 255, DeviceID.zero_fill_right_shift(_i_bq, 24), DeviceID.zero_fill_right_shift(_i_bq, 16) & 255, DeviceID.zero_fill_right_shift(_i_bq, 8) & 255, _i_bq & 255)
            if _i_bk == 512:
                _i_e += _i_bz
                _i_bz = ''
                _i_bk = 0
        return _i_e + _i_bz    
    
    @staticmethod
    def _if_q(_if_gt, _i_m):
        _i_e = DeviceID.toString16(_if_gt)
        if _i_m:
            return DeviceID._if_ac(_i_e, _i_m)
        else:
            return _i_e
        
    @staticmethod
    def _if_ac(_i_al, _if_gv):
        _i_m = ""
        _i_n = _if_gv - len(_i_al)
        while len(_i_m) < _i_n:
            _i_m += "0"
        return _i_m + _i_al
        

    @staticmethod
    def zero_fill_right_shift(v,n):
        return (v % 0x100000000) >> n

    @staticmethod
    def addOne(value):
        value += 1
        return value
    
    @staticmethod
    def fromCharCode(*args): return ''.join(map(chr, args))

    @staticmethod
    def toString16(num):
        return hex(num)[2:]
