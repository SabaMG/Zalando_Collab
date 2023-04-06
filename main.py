from zalando import ZALANDO

url = "https://www.zalando.fr/abercrombie-and-fitch-pant-going-everywhere-pantalon-classique-olive-a0f22e037-n11.html"
task = {"profile":"test","URL":url, "payment_method": "cc","ACCOUNT_EMAIL":"macouille@gmail.com","ACCOUNT_PASSWORD":"macouille","DOMAIN":"FR","EXCLUSIVE":"yes", "tasknumber":0, "proxy":None,"SIZE":"45", "discordid":"discord", "webhook":"https://discord.com/api/webhooks/1083398344371613726/08JzQYXIhP_iHgcvZXIHEwWuXG32ZXPHYhK_xt6UOvvuuSL5DiFXhJK7bNpLlXcpVpSm"}

zal = ZALANDO(task)

