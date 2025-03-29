from scrapp_arkham import *

#les adresses déjà classées
suspicious_addrs = ["1KsiEH5ZrfS3XhLVUU758rMKnP65kz2GYz","13sBMhTkri6be75TVQKHqtUo3LuLJRaY8p", "bc1qzkp563zxxcwu8dqv7n9k7673syx6d38k2l8lph"]
# tags collectés après scrapping en utilisant les adresses déjà classés de M.Conchon
suspicious_tags= ["Suspicious", "Ransomware"]

def collect_tags():
    res = []
    for addr in suspicious_addrs:
        tags = scrapp_tags(addr)
        res.extend(tags)

    return res


