
from discord_webhook import DiscordWebhook, DiscordEmbed

try: 
    from src.functions.settings import *
except ImportError: 
    from ..functions.settings import *
try: 
    from src.functions.api import *
except ImportError: 
    from ..functions.api import *

try: 
    from src.functions.notifications import *
except ImportError: 
    from ..functions.notifications import *

def webhook_public(webhook_fields:dict,img:str=None, title:str="Test Success 🎉", url:str=None):
    """
    sending a webhook to #public-success

    :param webhook_fields-> {"name":"value",...} for discord embed fields
    :param img -> img url for the thumbnail
    :param url -> url embedded in the title
    """
    pass

# ------------------------------------------------------------------------------- #

def webhook_private(webhook_fields:dict,img:str=None,url:str=None,success:str=True,profile_webhook:str="",title=None,product_url=None):
    """
    sending a webhook to the private webhook

    :param webhook_fields-> {"name":"value",...} for discord embed fields
    :param img -> img url for the thumbnail
    :param url -> url embedded in the title
    """
    pass


def webhook_other(webhook_fields:dict,img:str=None, title:str="Awaiting Action", url:str=None, profile_webhook:str="", color:int=242424):
    """
    :param webhook_fields-> {"name":"value",...} for discord embed fields
    :param img -> img url for the thumbnail
    :param url -> url embedded in the title
    """
    pass

def defaultWebhook(store,product,price,payment:float,size,email,profile,discordid,img,producturl,title="Successful Checkout!",checkouturl=None,scraper=None,profile_webhook=""):
    """
        default Webhook which sends Private and Public Webhook in one Take
        Only thing you have to pay attention to: product price needs to be an int / float
    """
    pass