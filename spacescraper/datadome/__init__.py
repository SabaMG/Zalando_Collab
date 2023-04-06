import random
import json
import time
import math
import numpy as np
import urllib.parse
import requests
try:
    from src.functions.settings import resource_path
except Exception:
    resource_path = lambda x : f"./{x}"

class DataDome():
    """
    Datadome Analyze Data Generator
    """
    def __init__(self, ddk : str, ddv: str, domain : str, referer : str, session : requests.Session, cookie : str):
        """
        Initialize the Generator

        Args:
            ddk (str): Datadome Key
            ddv (str): Datadome Version
            domain (str): Domain
            referer (str): Referer
            session (requests.Session): Session
            cookie (str): Cookie
        """
        # Datadome key
        self.ddk = ddk

        # Datadome version
        self.ddv = ddv

        # Datadome Cookie
        self.cid = cookie

        # Domain
        self.domain = domain

        # Referer
        self.referer = referer
        self.request = referer.split(domain)[1]

        # Devices
        self.device = DataDome.getDevice()
        self.navigator = self.device["navigator"]
        self.screen = self.device["screen"]
        self.uar = session.headers["user-agent"]
        self.version = self.uar.split("Chrome/")[1].split(".")[0]
        if "Mac" in self.uar:
            self.platform = 'macOS'
        elif "Windows" in self.uar:
            self.platform = 'Windows'
        elif "Linux" in self.uar:
            self.platform = 'Linux'
        elif "CrOS" in self.uar:
            self.platform = 'Chrome OS'
        else:
            self.platform = 'Unknown'

        self.getGraphics()
        self.getScreen()

        # Session
        self.session = session


    @staticmethod
    def getDevice():
        """
        Gets random device information

        Returns:
            dict: device information
        """
        path = resource_path('spacescraper/data/devices.json')
        with open(path) as devices_file:
            devices = json.load(devices_file)
            return random.choice(devices)
        
    def getScript(self):
        """
        Requests the datadome script
        """
        headers = {
            "sec-ch-ua": self.session.get_chrome_sec_ch_ua(self.version),
            "sec-ch-ua-mobile": "?0",
            "user-agent": self.uar,
            "sec-ch-ua-platform": f'"{self.platform}"',
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-dest": "script",
            "referer": f"https://{self.domain}/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "de-DE,de;q=0.9",
            "cookie": ""
        }
        self.session.get("https://js.datadome.co/tags.js", headers=headers)

    def postData(self):
        """
        Post inital data to datadome
        """
        # Generation Time
        self.ttst = round(random.uniform(8,40),15)
        self.tagpu = round(self.ttst - (0.20 * self.ttst),14)

        data = self.generateData()

        headers = {
                "connection": "keep-alive",
                "content-length": str(len(data)),
                "sec-ch-ua": self.session.get_chrome_sec_ch_ua(self.version),
                "sec-ch-ua-platform": f'"{self.platform}"',
                "sec-ch-ua-mobile": "?0",
                "user-agent": self.uar,
                "content-type": "application/x-www-form-urlencoded",
                "accept": "*/*",
                "origin": f"https://{self.domain}",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": f"https://{self.domain}/",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "cookie":""
            }

        res = self.session.post("https://api-js.datadome.co/js/", data=data, headers=headers)
        if res:
            datadomeJson = res.json()
            datadomeValue = datadomeJson["cookie"].split("=", maxsplit=1)[1].split(";", maxsplit=1)[0]
        else:
            datadomeValue = self.cid

        # Set Cookie
        self.cid = datadomeValue
    
    def postEvent(self):
        """
        Posts event data to datadome
        """
        data = self.generateData(event=True)

        headers = {
                "connection": "keep-alive",
                "content-length": str(len(data)),
                "sec-ch-ua": self.session.get_chrome_sec_ch_ua(self.version),
                "sec-ch-ua-platform": f'"{self.platform}"',
                "sec-ch-ua-mobile": "?0",
                "user-agent": self.uar,
                "content-type": "application/x-www-form-urlencoded",
                "accept": "*/*",
                "origin": f"https://{self.domain}",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": f"https://{self.domain}/",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "cookie":""
            }

        res = self.session.post("https://api-js.datadome.co/js/", data=data, headers=headers)
        if res:
            datadomeJson = res.json()
            datadomeValue = datadomeJson["cookie"].split("=", maxsplit=1)[1].split(";", maxsplit=1)[0]
        else:
            datadomeValue = self.cid

        # Set Cookie
        self.cid = datadomeValue
    
    def generateData(self, event : bool = False):
        """
        Generates data for datadome
        
        Args:
            event (bool, optional): If event data should be generated. Defaults to False.
        
        Returns:
            dict: Data
        """
        # jsType
        self.jsType = "ch"

        self.jset = int(time.time() * 1000)

        # Events
        self.events = []
        self.eventCounters = []


        jsData = {
            "ttst": self.ttst,
            "ifov":False,"log2":False,"wdif":False,"wdifrm":False,"log1":False,
            "br_h": self.br_h,
            "br_w": self.br_w,
            "br_oh": self.br_oh,
            "br_ow": self.br_ow,
            "nddc": self.isCookie(),  #is Cookie
            "rs_h": self.rs_h,
            "rs_w": self.rs_w,
            "rs_cd": self.rs_cd,
            "phe":False,"nm":False,"jsf":False,
            "ua": self.uar,
            "lg": self.navigator["language"],
            "pr": self.device["window"]["devicePixelRatio"],
            "hc": 10,
            "ars_h": self.ars_h,
            "ars_w": self.ars_w,
            "tz": -60,
            "str_ss":True,"str_ls":True,"str_idb":True,"str_odb":True,"plgod":False,
            "plg": len(self.navigator["plugins"]),
            "plgne":True,"plgre":True,"plgof":False,"plggt":False,"pltod":False,"hcovdr":False,"hcovdr2":False,"plovdr":False,"plovdr2":False,"ftsovdr":False,"ftsovdr2":False,"lb":False,
            "eva": 33, # For Chrome eval.toString().length = 33
            "lo":False,
            "ts_mtp": 0,
            "ts_tec":False,"ts_tsa":False,
            "vnd": self.navigator["vendor"],
            "bid": "NA", # Only for Firefox
            "mmt": self.getMimeTypes(),
            "plu": ",".join(self.navigator["plugins"]),
            "hdn":False,"awe":False,"geb":False,"dat":False,"med":"defined","aco":"probably","acots":False,"acmp":"probably","acmpts":True,"acw":"probably","acwts":False,"acma":"maybe","acmats":False,"acaa":"probably","acaats":True,"ac3":"","ac3ts":False,"acf":"probably","acfts":False,"acmp4":"maybe","acmp4ts":False,"acmp3":"probably","acmp3ts":False,"acwm":"maybe","acwmts":False,"ocpt":False,"vco":"probably","vcots":False,"vch":"probably","vchts":True,"vcw":"probably","vcwts":True,"vc3":"maybe","vc3ts":False,"vcmp":"","vcmpts":False,"vcq":"","vcqts":False,"vc1":"probably","vc1ts":True,
            "dvm": 8,
            "sqt":False,"so":"landscape-primary","wbd":False,"wdw":True,
            "cokys":"bG9hZFRpbWVzY3NpYXBwL=",
            "ecpc":False,"lgs":True,"lgsod":False,"psn":True,"edp":True,"addt":True,"wsdc":True,"ccsr":True,"nuad":True,"bcda":True,"idn":True,"capi":False,"svde":False,"vpbq":True,"ucdv":False,"spwn":False,"emt":False,"bfr":False,"dbov":False,"npmtm":False,
            "glvd":self.glvd,
            "tagpu": self.tagpu,
            "prm":True,"tzp":"Europe/Berlin","cvs":True,"usb":"defined","jset":int(self.jset/1000),
        }

        if event:
            self.jsType = "le"
            self.generateEvent()
            jsData["cfpfe"] = "RXJyb3I6IENhbm5vdCByZWFkIHByb3BlcnRpZXMgb2YgbnVsbCAocmVhZGluZyAndG9TdHJpbmcnKQ=="
            jsData["stcfp"] = "IChodHRwczovL2Nkbi5jb29raWVsYXcub3JnL3NjcmlwdHRlbXBsYXRlcy82LjI5LjAvb3RCYW5uZXJTZGsuanM6NzoxNzM1KQogICAgYXQgaHR0cHM6Ly9jZG4uY29va2llbGF3Lm9yZy9zY3JpcHR0ZW1wbGF0ZXMvNi4yOS4wL290QmFubmVyU2RrLmpzOjc6Njcz"
            jsData["dcok"] = self.domain.replace("www","")
            self.getMouseData()
            if self.eventCounters["mouse move"] > 0:
                jsData["mp_cx"] = self.mp_cx
                jsData["mp_cy"] = self.mp_cy
                jsData["mp_tr"] = self.mp_tr
                jsData["mp_mx"] = self.mp_mx
                jsData["mp_my"] = self.mp_my
                jsData["mp_sx"] = self.mp_sx
                jsData["mp_sy"] = self.mp_sy
                jsData["mm_md"] = self.mm_md

            jsData["tbce"] = random.randint(90,150)
            jsData["es_sigmdn"] = self.es_sigmdn
            jsData["es_mumdn"] = self.es_mumdn
            jsData["es_distmdn"] = self.es_distmdn
            jsData["es_angsmdn"] = self.es_angsmdn
            jsData["es_angemdn"] = self.es_angemdn

        
        data = {
            "jsData": json.dumps(jsData, separators=(',', ':')),
            #"events": json.dumps(self.events, separators=(',', ':')),
            "eventCounters": json.dumps(self.eventCounters, separators=(',', ':')),
            "jsType": self.jsType,
            "cid": self.cid,
            "ddk": self.ddk,
            "Referer": urllib.parse.quote_plus(self.referer),
            "request": urllib.parse.quote_plus(self.request),
            "responsePage": "origin",
            "ddv": self.ddv,
        }
        return data


    def isCookie(self):
        """
        Check if cookie is set

        Returns:
            int: 1 if cookie is set, 0 if not
        """
        if self.cid:
            return 1
        else:
            return 0
        
    def getMimeTypes(self):
        """
        Get all mime types

        Returns:
            str: all mime types
        """
        mt = self.navigator["mimeTypes"]
        mmt = ",".join(t["type"] for t in mt)
        return mmt
    
    def getGraphics(self):
        """
        Gets graphics card information
        """
        self.glvd = self.device["wv"]
        self.glrd = self.device["wr"]
        
    def getScreen(self):
        """
        Gets screen information
        """
        self.br_h = self.device["window"]["innerHeight"]
        self.br_w = self.device["window"]["innerWidth"]
        self.br_oh = self.device["window"]["outerHeight"]
        self.br_ow = self.device["window"]["outerWidth"]

        self.rs_h = self.screen["height"]
        self.rs_w = self.screen["width"]
        self.rs_cd = self.screen["colorDepth"]

        self.ars_h = self.screen["availHeight"]
        self.ars_w = self.screen["availWidth"]


    def getMouseData(self):
        """Generates mouse data"""
        self.mp_cx = random.randint(200, 900)
        self.mp_cy = random.randint(200, 500)
        self.mp_tr = True
        self.mp_mx = random.randint(-40,40)
        self.mp_my = random.randint(-40,40)
        self.mp_sx = self.mp_cx + random.randint(100,300)
        self.mp_sy = self.mp_cy + random.randint(100,300)
        self.mm_md = random.randint(1,100)
        mouseEvents = [e for e in self.events if e["message"] == "mouse move"]
        mouseEventCounter = self.eventCounters["mouse move"]
        es_sigmdn_array = []
        es_mumdn_array = []
        es_distmdn_array = []
        startAngels = []
        endAngels = []
        for e in mouseEvents:
            x = math.log(e["date"])
            q = mouseEventCounter
            y = math.log(e["date"]) * math.log(e["date"])
            es_sigmdn_array.append(round(np.longfloat(math.sqrt((q*y-x*x)/(q*(q-1))) / 10000),21))
            es_mumdn_array.append(x/q)

            if q < 4:
                D =  q - 1
            else:
                D = 3
            E = mouseEvents[D]
            F = mouseEvents[len(mouseEvents) - D - 1]
            def calculateAngle(m, p, q, u):
                v = q - m
                w = u - p
                x = math.acos(v / math.sqrt(v * v + (w * w)))
                if w < 0:
                    return -x
                return x
            startAngels.append(calculateAngle(mouseEvents[0]["source"]["x"], mouseEvents[0]["source"]["y"], E["source"]["x"], E["source"]["y"]))
            endAngels.append(calculateAngle(mouseEvents[-1]["source"]["x"], mouseEvents[-1]["source"]["y"], F["source"]["x"], F["source"]["y"]))

        
        for i in range(len(mouseEvents)):
            try:
                diff_x = mouseEvents[i+1]["source"]["x"] - mouseEvents[i]["source"]["x"]
                diff_y = mouseEvents[i+1]["source"]["y"] - mouseEvents[i]["source"]["y"]
                es_distmdn_array.append(math.sqrt(diff_x**2 + diff_y**2))
            except IndexError:
                pass
        
        def getValue(sorted_array):
            u = (len(sorted_array) - 1) * 50 / 100
            v = math.floor(u) + 1
            try:
                if sorted_array[v] != 0:
                    w = u - v
                    try:
                        return str(sorted_array[v] + w * (sorted_array[v + 1] - sorted_array[v]))
                    except IndexError:
                        return str(sorted_array[v])
                else:
                    return str(sorted_array[v])
            except IndexError:
                return None
        
        self.es_sigmdn = getValue(sorted(es_sigmdn_array))
        self.es_mumdn = getValue(sorted(es_mumdn_array))
        self.es_distmdn = getValue(sorted(es_distmdn_array))
        self.es_angsmdn = getValue(sorted(startAngels))
        self.es_angemdn = getValue(sorted(endAngels))

    
    def generateEvent(self):
        """
        Generate a random event
        """
        # Mouse move
        startingPos = [random.randint(0, self.br_w), random.randint(0, self.br_h)]
        currentPos = startingPos
        endingPos = [random.randint(0, self.br_w), random.randint(0, self.br_h)]
        x = [startingPos[0]]
        y = [startingPos[1]]
        while endingPos[0] != currentPos[0] and len(x) < 500:
            deltaPos1 = (random.randint(2, 8), random.randint(2, 8))
            deltaPos2 = (random.randint(5, 12), random.randint(5, 12))
            deltaPosList = [deltaPos1, deltaPos2]
            deltaPos = random.choice(deltaPosList)
            if currentPos[0] < endingPos[0] and endingPos[0] - currentPos[0] > 50:
                currentPos[0] += deltaPos[0] + random.randint(-100, 100)
            elif currentPos[0] < endingPos[0] and endingPos[0] - currentPos[0] < 50:
                currentPos[0] += endingPos[0] - currentPos[0]
            elif currentPos[0] > endingPos[0] and currentPos[0] - endingPos[0] > 50:
                currentPos[0] -= deltaPos[0] + random.randint(-100, 100)
            elif currentPos[0] > endingPos[0] and currentPos[0] - endingPos[0] < 50:
                currentPos[0] -= currentPos[0] - endingPos[0]
            if currentPos[0] > 0:
                x.append(currentPos[0])

        y = np.linspace(startingPos[1], endingPos[1], len(x), dtype=int)
        
        self.events = [{"source":{"x":int(x[i]),"y":int(y[i])},"message":"mouse move","date":None,"id":0}for i in range(len(x))]

        # Mouse click
        if random.random() > 0.2 and len(x) > 50:
            for i in range(random.randint(1, 10)):
                event = random.choice(self.events)
                event["message"] = "mouse click"
                event["id"] = 1
        
        # Scroll event
        scrollStart = random.randint(1, 10)
        scrollCurrent = scrollStart
        steps = random.randint(30, 200)
        scrollY = [scrollStart]
        for _ in range(steps):
            if scrollCurrent > 250:
                scrollCurrent -= random.randint(10, 100)
            else:
                scrollCurrent += random.randint(10, 100)
            scrollY.append(scrollCurrent)
            
        scrollEvents = [{"source":{"x":0,"y":scrollY[i]},"message":"scroll","date":None,"id":2} for i in range(len(scrollY))]
        self.events.extend(scrollEvents)
        
        # Set event dates
        for i, event in enumerate(self.events):
            event["date"] = self.jset - (len(event)-i)*0.5
        
        # Event counter
        self.eventCounters = {"mouse move":len([i for i,e in enumerate(self.events) if e["message"] == "mouse move"]),"mouse click":len([i for i,e in enumerate(self.events) if e["message"] == "mouse click"]),"scroll":len([i for i,e in enumerate(self.events) if e["message"] == "scroll"]),"touch start":0,"touch end":0,"touch move":0,"key down":0,"key up":0}