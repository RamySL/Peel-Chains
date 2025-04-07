from pyvis.network import Network
from mixers import *
#import scrapp_arkham
import time
#from collect_tags import *
import json

net = Network(notebook=True, directed=True,height="100vh", width="100%")
TAGS_BINANCE = None
#Couleur par défaut des noeuds
DEFAULT_COLOR = '#0000ff'
with open('../json/exchange_tags.json', 'r') as file:
    TAGS_BINANCE = json.load(file)

'''
Attend un graphe sous forme de dictionnaire avec comme clés : nodes et edges.
Elle est Hardcode avec la structure dans le fichier ./mixers.py
'''
def render(graph:dict, dst:str):
  global net
  tags = []
  first = True # pour colorer diff la premiere tx
  for e in graph['edges']:
      
      from_ = e['from']
      to_ = e['to']
      if (e["input"]):
          #from_ = e['input_id']
          #tags = scrapp_arkham.scrapp_tags(e['from'])
          #time.sleep(1) # pour ne pas a être bloqué

          #addr
          net.add_node(from_,label=" ", color=color(tags), title=format_infos(e['from'], tags))
          #tx
          if first:
              net.add_node(to_,label=" ",color="#c002fa",shape='square', title=format_infos(to_))
              first = False
          else: 
            if(e["DAG"]):
              net.add_node(to_,label=" ",color="#ff0000",shape='square', title=format_infos(to_,["DAG"]))
            else:
              net.add_node(to_,label=" ",color="#00ffbf",shape='square', title=format_infos(to_))

          net.add_edge(from_, to_,label=e['label'], color="#000000") 


      else:
          #tags = scrapp_arkham.scrapp_tags(e['to'])
          #time.sleep(1) # pour ne pas a être bloqué
        #tx
        if first:
          net.add_node(from_,label=" ",color="#c002fa",shape='square', title=format_infos(from_))
          first = False
        else:
          net.add_node(from_, label=" ", color="#00ffbf", shape='square', title=format_infos(from_))
        #addr
        net.add_node(to_, label=" ",color=color(tags), title=format_infos(to_,tags))
        net.add_edge(from_, to_,label=e['label'])


  #scrapp_arkham.quit_driver()
  net.show(dst)

'''
Donne une couleur pour colorier le noeud avec selon les tags de son adresse
'''
def color (tags):
    for tag in tags:
        if tag in TAGS_BINANCE:
            return '#ff0000'
    return DEFAULT_COLOR

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
   # Ouvrir le fichier edges.json et charger son contenu
    try:
        with open('edges.json', 'r') as file:
            data = json.load(file)
            edges = data.get("edges", [])  # Récupérer la liste des arêtes
            render({"edges" : edges})
    except FileNotFoundError:
        print("Erreur : Le fichier 'edges.json' n'existe pas.")
    except json.JSONDecodeError:
        print("Erreur : Le fichier 'edges.json' contient des données invalides.")
   
