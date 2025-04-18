import sys
import requests
import json
from abc import ABC, abstractmethod
from collections import deque
from scrapp_arkham import scrapp_tags
import heapq
from itertools import count
import networkx as nx
"""
Module de génération du graphe.
"""

BASE_URL = "https://api.blockchain.info/haskoin-store/btc"

#### Définitions de classes ##########################################################################
######################################################################################################
class IterStructure(ABC):
    """
    Classe abstraite qui définie l'interface pour implémenter la structure qui va stocker les noeuds
    du graphe pendant le parcours.
    """
    def __init__ (self,s):
        self.s = s
    
    @abstractmethod
    def push(self):
        pass
    @abstractmethod
    def pop(self):
        pass
    @abstractmethod
    def peek(self):
        pass

    def is_empty(self)->bool:
        return not(self.s)
    
class IterDPS (IterStructure):
    """
    Classe pour implémnter le parcours en profondeur
    """

    """
    S: structure qui va stocker les noeuds sur lesquels il faut itérer
    """
    def __init__ (self):
        super().__init__(deque())
    
    def push(self, node)->None:
        self.s.append(node)

    def pop(self):
        return self.s.pop()
    
    def peek(self):
        res = self.pop()
        self.push(res)
        return res
    def __str__(self):
        return "DPS"
    
    
  
class IterBFS (IterStructure):
    """
    Classe pour implémnter le parcours en largeur
    """

    """
    S: structure qui va stocker les noeuds sur lesquels il faut itérer
    """
    def __init__ (self):
        super().__init__(deque())

    def push(self, node)->None:
        self.s.append(node)

    def pop(self):
        return self.s.popleft()
    
    def peek(self):
        res = self.pop()
        self.s.appendleft(res)
        return res

    def __str__(self):
        return "BFS"
    

class IterPriority(IterStructure):
    '''
    Implémentation d'une file de priorité avec un tas binaire. 
    La priorité est pour les outputs avec le plsu de valeur
    c'est tas-min.

    Les elts qu'elle prend doivent etre de type : 
    {"tx_src": tx_src, 
    "addr": addr, 
    "tx_dst": tx_dst,
    "v_out":out["value"], 
    #"v_inp": v_inp
    "v_inp": out["value"]
    })
    '''
    # max pour tas max ou tas min (entier soit -1 soit 1)
    # -1 pour tas max, 1 pour tas min
    def __init__(self, tas_max=-1):
        # utile pour éviter que l'ordre lexico ne compare des elts qui ne peuvent pas être ordonnés dans le push
        self.tas_max = tas_max
        self.counter = count()
        super().__init__([])
    
    def push(self, item):
        """
        Ajoute un élément à la file de priorité.
        un tuple (priority, data), où priority est un nombre.
        """
        heapq.heappush(self.s, ((self.tas_max * item["v_out"],next(self.counter)), item))

    def pop(self):  
        """
        retourne l'elt avec la plus haute priorité (plus petite valeur)
        """
        return heapq.heappop(self.s)[1]

    def peek(self):
        
        return self.s[0]

    def __str__(self):
        return "PQ"

###########################################################################################
######### Définition de fonctions ######################################################### 

'''
La structure que le render_graph.py attend pour les edges est la sivantes : 

    edge = { "from": str,
            "to": str,
            "label": str (f"{curr['v_out'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC"),
            "input": bool,
            "DAG": bool,
            "exchange": bool,
            "tags": list
            }
    Donc en plus d'ajouter les arrêtes dans le DiGraph() avec le src et dst en passe en méta donnée la structure précédentes
    comme ça elle sera utilisée par la vue (elle est passé dans un champ "meta")
'''

'''
Retourne vrai si il ya un dag dans le graphe et marque la transaction comme étant un dag
'''
def is_dag (graph, txid):
    for e in graph["edges"]:
        # invariant que on va passer par le premier edge en premier et l'algo ajoute d'abord
        # les inputs donc c'est dans e["to"] qu'il ya le txid 
        # Il suffit de modifier le DAG = True que du premier, de tte les manière c'est le premier 
        # affichage qui va rester
        if e["to"] == txid:
            print(f'DAG {txid}')
            e["DAG"] = True
            return True
    return False


def graph_from_depth(txid:str, depth:int, structure:IterStructure, write=False, dst="edges.json"):
    graph = nx.DiGraph()

    if write:
        with open(dst, 'w') as file:
            json.dump({"edges": []}, file)
    # on push txid et la profondeur courante
    structure.push((txid,0))
    while not (structure.is_empty()) :
        
        (txid, curr_d) = structure.pop()
        tx_data = fetch_transaction(txid)                
        #dag = is_dag(graph, txid)
        dag = False
        if not dag :    
            for inp in tx_data['inputs']:
                addr = inp['address']
                if not inp['coinbase']:
                    edge = {
                        "from": addr,
                        "to": txid,
                        "label": f"{inp['value'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC",
                        "input": True,
                        "DAG": False
                    }
                    graph.add_edge(addr, txid, meta=edge)
                    if write:
                        append_to_json_list(dst, "edges", edge)


            for out in tx_data['outputs']:
                addr = out['address']
                if addr:
                    edge = { "from": txid,
                            "to": addr,
                            "label": f"{out['value'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC",
                            "input": False,
                            "DAG": False
                            }
                    graph.add_edge(txid,addr, meta=edge )
                    if write:
                        append_to_json_list(dst, "edges", edge)
                    # redendant de tester à chaque fois current depth
                    if curr_d < depth and out.get("spent") and out.get("spender"):
                        structure.push((out["spender"]["txid"], curr_d+1))
        
    return graph
'''
Type de dict à ajouter dans la structure de parcours : 
{tx_src: id d'une tx, addr: adresse, tx_dst: id d'une tx, v_out montant de l'outout depuis src, v_inp: }
tq tx_src est une transaction dans laquelle addr était un output qui est dépensé dans tx_dst.
On attend des arrêtes entre les trois
'''
def graph_from_nb_nodes(txid:str, n_nodes:int, structure:IterStructure, write=False, dst="edges.json"):
    graph = nx.DiGraph()
    # compteur de noeuds
    cpt = 0
    explore_tx(txid, structure)

    while (cpt < n_nodes and not structure.is_empty()):
        
        curr = structure.pop()
        tags = scrapp_tags(curr["addr"])
        exch = any(tag in ["Centralized Exchange","Hot Wallet"] for tag in tags)
        if(exch):
            print("exchange : " + curr["addr"])
        cpt += 1 

        edge = { "from": curr["tx_src"],
                                "to": curr["addr"],
                                "label": f"{curr['v_out'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC",
                                "input": False,
                                "DAG": False,
                                "exchange": exch,
                                "tags": tags
                                }
        graph.add_edge(curr["tx_src"], curr["addr"], meta=edge )

        if(curr["tx_dst"] and not exch):  
            #dag = is_dag(graph, curr["tx_dst"])
            dag = False
            if not dag : 
                explore_tx(curr["tx_dst"], structure)

            edge = { "from": curr["addr"],
                                "to": curr["tx_dst"],
                                "label": f"{curr['v_inp'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC",
                                "input": True,
                                "DAG": False,
                                "exchange": False,
                                "tags": tags
                                }

            graph.add_edge(curr["addr"], curr["tx_dst"], meta=edge )
        
    return graph

'''
Parcoure les output d'une transaction et les ajoute pour le traitement dans la structure.
pour Les BTC entre tx_src -> addr et entre addr -> tx_dst on utilise les même (on ignore les frais) parce que
ce n'est pas une info pertinente
'''
def explore_tx (tx_src, structure):
    tx_data = fetch_transaction(tx_src)
    
    for out in tx_data['outputs']:
        tx_dst = None
        addr = out['address']
        #v_inp = 0
        if(out["spent"] and out["spender"]):
            tx_dst = out["spender"]["txid"]
            #v_inp = get_inp_val(tx_src, tx_dst, addr)

        structure.push({"tx_src": tx_src, 
                        "addr": addr, 
                        "tx_dst": tx_dst,
                        "v_out":out["value"], 
                        #"v_inp": v_inp
                        "v_inp": out["value"]
                        })

'''
recup la valeur en satoshi, qu'a ramené addr en tant qu'input de tx_dst dépensé à partir de tx_src
'''
def get_inp_val (tx_src, tx_dst, addr):
    tx_data = fetch_transaction(tx_dst)
    for inp in tx_data["inputs"]:
        if (inp["txid"] == tx_src):
            return inp["value"]
    # pas censé arriver
    return None 
        

   
def fetch_transaction(txid):
    url = f"{BASE_URL}/transaction/{txid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def append_to_json_list(file_path, list_name, item):
    """
    Ouvre un fichier JSON, ajoute un élément à une liste spécifique, et réécrit le fichier.

    :param file_path: Chemin du fichier JSON.
    :param list_name: Nom de la liste dans le fichier JSON.
    :param item: Élément à ajouter à la liste.
    """
    try:
        with open(file_path, 'r+') as file:
            data = json.load(file)
            
            if list_name not in data:
                data[list_name] = []
            
            data[list_name].append(item)
            
            file.seek(0)  # Revenir au début du fichier
            json.dump(data, file, indent=4)
            file.truncate()  # Supprimer le contenu restant si le nouveau contenu est plus court
    except Exception as e:
        print(f"Erreur lors de l'ajout à la liste JSON : {e}")

#########################################################################################################

if __name__ == "__main__":
    tx = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'
    print(graph_from_depth(tx,1, IterBFS())["nodes"])
