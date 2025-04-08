from pyvis.network import Network
from mixers import *
#import scrapp_arkham
import time
#from collect_tags import *
import json

net = Network(notebook=True, directed=True,height="100vh", width="100%")
TAGS_RANSOME = None

with open('../json/ransom_tags.json', 'r') as file:
    TAGS_RANSOME = json.load(file)

# Couleurs des noeuds
DEFAULT_ADDR = '#0000ff'
RANSOME_ADDR = "#ff0000"
EXCHANGE_ADDR = "#000000"
DEFAULT_TX = "#00ffbf"
FIRST_TX = "#c002fa"
DAG_TX = "#ff0000"

##
first = True # pour colorer diff la premiere tx

'''
Attend un graphe sous forme de dictionnaire avec comme clés : nodes et edges.
Elle est Hardcode avec la structure dans le fichier ./mixers.py
'''
def render(graph:dict, dst:str):
  global net
  for e in graph['edges']:
      
      from_ = e['from']
      to_ = e['to']
      if (e["input"]):
          #addr
          net.add_node(from_,label=" ", color=color_addr(e["tags"], e["exchange"]), title=format_infos(e['from'], e["tags"]))
          #tx
          net.add_node(to_,label=" ",color=color_tx(e["DAG"]),shape='square', title=format_infos(to_))
          
          net.add_edge(from_, to_,label=e['label'], color="#000000") 

      else:
        #tx
        net.add_node(from_,label=" ",color=color_tx(e["DAG"]),shape='square', title=format_infos(from_))
        #addr
        net.add_node(to_, label=" ",color=color_addr(e["tags"],e["exchange"]), title=format_infos(to_,e["tags"]))

        net.add_edge(from_, to_,label=e['label'])

  net.show(dst)

'''
Donne une couleur pour colorier le noeud avec selon les tags de son adresse
'''
def color_addr (tags, exch):
    if exch:
       return EXCHANGE_ADDR
       
    for tag in tags:
        if tag in TAGS_RANSOME:
            return RANSOME_ADDR
        
    return DEFAULT_ADDR

def color_tx(dag):
  global first
  if first:
      first = False
      return FIRST_TX
  if dag :
      return DAG_TX
   
  return DEFAULT_TX

'''
Retoune les information sur le noeud pour les afficher dans le graphe
'''
def format_infos(id, tags=[]):
    return f"id/addr: {id} \n tags:{tags} "
    
# Plusieurs options peuvent être définies pour l'affichage
net.set_options('''
var options = {
  "edges": {
    "arrows": {
      "to": {
        "enabled": true,
        "scaleFactor": 1
      }
    }
  }
}
''')

if __name__ == "__main__":
    try:
        with open('edges.json', 'r') as file:
            data = json.load(file)
            edges = data.get("edges", [])  # Récupérer la liste des arêtes
            render({"edges" : edges})
    except FileNotFoundError:
        print("Erreur : Le fichier 'edges.json' n'existe pas.")
    except json.JSONDecodeError:
        print("Erreur : Le fichier 'edges.json' contient des données invalides.")
   
