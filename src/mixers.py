import sys
import requests
import json
from abc import ABC, abstractmethod
from collections import deque

"""
Module de génération du graphe.
"""

BASE_URL = "https://api.blockchain.info/haskoin-store/btc"
nb_dags = 0


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



def graph_from_tx(txid:str, depth:int, structure:IterStructure, write=False, dst="edges.json"):
    global nb_dags
    graph = { "nodes": [], "edges": [] }

    if write:
        with open(dst, 'w') as file:
            json.dump({"edges": []}, file)
    # on push txid et la profondeur courante
    structure.push((txid,0))
    while not (structure.is_empty()) :
        dag = False
        (txid, curr_d) = structure.pop()
        tx_data = fetch_transaction(txid)

        for e in graph["edges"]:
            # invariant que on va passer par le premier edge en premier et l'algo ajoute d'abord
            # les inputs donc c'est dans e["to"] qu'il ya le txid 
            # Il suffit de modifier le DAG = True que du premier, de tte les manière c'est le premier 
            # affichage qui va rester
            if e["to"] == txid:
                print(f'DAG {txid}')
                dag = True
                e["DAG"] = True
                break
                

        if not dag :    

            n = { "id": txid,
              "label": f"TX: {tx_data['txid'][:8]}...",
              "type": "transaction",
               "DAG": False }
            graph["nodes"].append(n)

            for inp in tx_data['inputs']:
                addr = inp['address']
                if not inp['coinbase']:
                    graph["nodes"].append({
                        "id": addr,
                        "label": f"A: {addr[:5]}...",
                        "type": "address"
                    })
                    edge = {
                        "from": addr,
                        "to": txid,
                        "label": f"{inp['value'] / 100_000_000:.4f} BTC",
                        "input": True,
                        "DAG": False
                        # Pour différencier différent inputs de la même personne.
                        #"input_id": f"{addr}{inp['txid']}{inp['output']}" 
                    }
                    graph["edges"].append(edge)
                    if write:
                        append_to_json_list(dst, "edges", edge)


            for out in tx_data['outputs']:
                addr = out['address']
                if addr:
                    node = {
                        "id": addr,
                        "label": f"A: {addr[:5]}...",
                        "type": "address"
                    }
                    graph["nodes"].append(node)
                    edge = { "from": txid,
                            "to": addr,
                            "label": f"{out['value'] / 100_000_000:.8f} BTC",
                            "input": False,
                            "DAG": False
                            }
                    graph["edges"].append(edge)
                    if write:
                        append_to_json_list(dst, "edges", edge)
                    # redendant de tester à chaque fois current depth
                    if curr_d < depth and out.get("spent") and out.get("spender"):
                        structure.push((out["spender"]["txid"], curr_d+1))
        
    return graph
   
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


if __name__ == "__main__":
    tx = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'
    print(graph_from_tx(tx,1, IterBFS())["nodes"])
