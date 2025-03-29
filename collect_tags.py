from scrapp_arkham import *
import time
import json

'''
Collecte des tags mis par Arkham sur les adresses qui ont était utilisée pour des rançon etc 
'''

#les adresses déjà classées (rançon)
ransom_addrs = ["1KsiEH5ZrfS3XhLVUU758rMKnP65kz2GYz",
                "13sBMhTkri6be75TVQKHqtUo3LuLJRaY8p", 
                "bc1qzkp563zxxcwu8dqv7n9k7673syx6d38k2l8lph",
                ]
suspected_mixer = ["18h552tdEMq61a7byhoSnXWto98qqXkR7k",
                   "19qvaWW2qvuwkcyBJQGdBh4uUZ1hrJaLgh",
                   "1NUh4mZVBjBsWzDnmQcsjdrhVQrUPpof1L",
                   ]


def collect_tags (addrs:list)->list:
    res=[]
    for addr in addrs:
        tags = scrapp_tags(addr)
        time.sleep(2)
        for tag in tags:
            if tag not in res:
                res.append(tag)
    return res

def write_tags_to_json(tags, file_path="collected_tags.json"):
    with open(file_path, "w") as json_file:
        json.dump(tags, json_file, indent=4)

if __name__ == "__main__":
    write_tags_to_json(collect_tags(ransom_addrs), "ransom_tags.json")
    write_tags_to_json(collect_tags(suspected_mixer), "suspected_mixers_tags.json")



