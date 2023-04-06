import platform
import ctypes
import sys
version = ""
username = ""
def titelbar(message:str):
    global username,version
    message = message.replace("  -  ",f" {version} - {username} ")
    try:
        if " - MENU" in message:
            if username == "" and version == "":
                username,version = message.split("Test - ")[1].split(" - MENU")[0].split(" - ")[1],message.split("Test - ")[1].split(" - MENU")[0].split(" - ")[0]
        if platform.system() == 'Darwin':
            sys.stdout.write(f"\x1b]2;{message}\x07")
        elif platform.system() == 'Windows':
            ctypes.windll.kernel32.SetConsoleTitleW(message)
    except Exception:
        #running in dev mode
        pass

titel_data = {}
class MODULETITEL():
    global titel_data
    def __init__(self,data:dict):
        """
        example: 
        titelbar_example = MODULETITEL({
            "store":"Asos",
            "values": [
                "Task(s)",
                "Carts",
                "Failed",
                "Success"
                ]
            })
        """
        self.store = str(data["store"]).upper()
        del data["store"]
        try:
            titel_data[self.store]
        except:
            titel_data[self.store] = {}
            titelstring = f"Test - {version} - {username}"
            for value in data["values"]:
                titel_data[self.store][str(value).upper().strip()] = 0
                titelstring += f" - {value}: {titel_data[self.store][str(value).upper().strip()]}"
            titelbar(titelstring)
    def status_bar(self,data:str):
        """
            to add a Task:
                    titelbar_example.status_bar("Task(s)")
                or 
                    titelbar_example.status_bar("+Task(s)")
            
            to remove a Task:
                titelbar_example.status_bar("-Task(s)")
        """
        try:
            if data[0] == "-":
                titel_data[self.store][str(data[1:]).upper().strip()] -= 1
            else:
                if data[0] == "+":
                    titel_data[self.store][str(data[1:]).upper().strip()] += 1
                else:
                    titel_data[self.store][str(data).upper().strip()] += 1
            titelstring = f"Test - {version} - {username} - Store: {self.store.upper()}"
            for titel in titel_data[self.store]:
                titelstring += f" - {titel}: {titel_data[self.store][titel]}"
            titelbar(titelstring)
        except: pass
