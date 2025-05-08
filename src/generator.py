import sys
import requests
import json
from abc import ABC, abstractmethod
from collections import deque
from scrapp_arkham import scrapp_tags
import heapq
from itertools import count
import networkx as nx
from enum import Enum, auto


"""
Module de génération du graphe.
"""

BASE_URL = "https://api.blockchain.info/haskoin-store/btc"

#### Définitions de classes ##########################################################################
######################################################################################################


class Mode(Enum):
    """
    Mode de génération de graphe.
    NODE: génération de graphe avec un nombre de noeuds donné
    DEPTH: génération de graphe avec une profondeur donnée
    """
    NODE = auto()
    DEPTH = auto()

class IterStructure(ABC):
    """
    Classe abstraite qui définie l'interface pour implémenter la structure qui va stocker les noeuds
    du graphe pendant le parcours.
    mode: NODE ou DEPTH
    n: nombre de noeuds à généré ou profondeur maximal selon mode
    cpt: le compteur qui ne doit pas dépasser n
    """
    def __init__ (self, s, mode:Mode, n: int):
        self.s = s
        self.mode = mode
        self.n = n
        if mode == Mode.NODE:
            self.cpt = 0
        else:
            self.curr_dpth = 0


    @abstractmethod
    def peek(self):
        pass
    
    
    def push(self, node, add):
         '''
         add: est la fonction d'ajout dans la structure
         '''
         match self.mode:
            case Mode.DEPTH:
                if self.curr_dpth < self.n :
                    add((node, self.curr_dpth+1))

            case Mode.NODE:
                if self.cpt < self.n:
                    add(node)
                    
    def pop(self, rem):
        '''
         rem: est la fonction pour enlever de la structure
        '''
        if self.mode == Mode.DEPTH:
            (node, self.curr_dpth) = rem()
            return node
        else:
            self.cpt += 1
            return rem()
        
    def end(self)->bool:
        '''
        Dit si le parcours est terminé
        '''
        match self.mode:
            case Mode.NODE:
                return self.is_empty() or self.cpt >= self.n
            case Mode.DEPTH:
                return self.is_empty()

    def is_empty(self)->bool:
        return not(self.s)
    
class IterDPS (IterStructure):
    """
    Classe pour implémnter le parcours en profondeur
    """

    """
    S: structure qui va stocker les noeuds sur lesquels il faut itérer
    """
    def __init__ (self, mode:Mode, n:int):
        super().__init__(deque(), mode, n)
    
    def push(self, node)->None:
        super().push(node, self.s.append)
        
    def pop(self):
        return super().pop(self.s.pop)    
    
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
    def __init__ (self, mode:Mode, n:int):
        super().__init__(deque(), mode, n)

    def push(self, node)->None:
        super().push(node, self.s.append)

    def pop(self):
        return super().pop(self.s.popleft)    
        
    def peek(self):
        res = self.pop()
        self.s.appendleft(res)
        return res

    def __str__(self):
        return "BFS"
    

class IterPriority(IterStructure):
    '''
    Implémentation d'une file de priorité avec un tas binaire. 
    La priorité est défini pour les valeurs d'outputs.
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
    # tas_max: pour tas max ou tas min (entier soit -1 soit 1)
    # -1 pour tas max, 1 pour tas min
    def __init__(self, mode:Mode, n:int, tas_max=-1):
        self.tas_max = tas_max
        # utile pour éviter que l'ordre lexico ne compare des elts qui ne peuvent pas être ordonnés dans le push
        self.counter = count()
        super().__init__([], mode, n)
    
    def push(self, item):
        """
        Ajoute un élément à la file de priorité.
        un tuple (priority, data), où priority est un nombre.
        """
        super().push(((self.tas_max * item["v_out"],next(self.counter)), item), lambda x: heapq.heappush(self.s, x))
        

    def pop(self):  
        """
        retourne l'elt avec la plus haute priorité (plus petite valeur)
        """
        return super().pop(lambda: heapq.heappop(self.s))[1]    

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


def gen_graph(txid:str, structure:IterStructure):
    '''
        Type de dict à ajouter dans la structure de parcours : 
        {tx_src: id d'une tx, addr: adresse, tx_dst: id d'une tx, v_out montant de l'outout depuis src, v_inp: }
        tq tx_src est une transaction dans laquelle addr était un output qui est dépensé dans tx_dst.
        On attend des arrêtes entre les trois
    '''
    graph = nx.DiGraph()
    explore_tx(txid, structure)

    while not (structure.end()) :
        
        curr = structure.pop()
        tags = scrapp_tags(curr["addr"])
        exch = any(tag in ["Centralized Exchange","Hot Wallet"] for tag in tags)

        if(exch):
            print("exchange : " + curr["addr"])

        edge = { 
            "from": curr["tx_src"],
            "to": curr["addr"],
            "label": f"{curr['v_out'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC",
            "input": False,
            "DAG": False,
            "exchange": exch,
            "tags": tags
            }
        graph.add_edge(curr["tx_src"], curr["addr"], meta=edge)

        if(curr["tx_dst"] and not exch):  
            #dag = is_dag(graph, curr["tx_dst"])
            dag = False
            if not dag : 
                explore_tx(curr["tx_dst"], structure)

            edge = { 
                "from": curr["addr"],
                "to": curr["tx_dst"],
                "label": f"{curr['v_inp'] / 100_000_000:.4f}".rstrip('0').rstrip('.') + " BTC",
                "input": True,
                "DAG": False,
                "exchange": False,
                "tags": tags
                }

            graph.add_edge(curr["addr"], curr["tx_dst"], meta=edge )
        
        
    return graph


def explore_tx (tx_src, structure):
    '''
    Parcoure les output d'une transaction et les ajoute pour le traitement dans la structure.
    pour Les BTC entre tx_src -> addr et entre addr -> tx_dst on utilise les même (on ignore les frais) parce que
    ce n'est pas une info pertinente
    '''
    tx_data = fetch_transaction(tx_src)    
    for out in tx_data['outputs']:
        tx_dst = None
        addr = out['address']
        if(out["spent"] and out["spender"]):
            tx_dst = out["spender"]["txid"]

        structure.push({
            "tx_src": tx_src, 
            "addr": addr, 
            "tx_dst": tx_dst,
            "v_out":out["value"], 
            "v_inp": out["value"]
        })

def fetch_transaction(txid):
    url = f"{BASE_URL}/transaction/{txid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

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

#########################################################################################################

if __name__ == "__main__":
    tx = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'
    print(graph_from_depth(tx,1, IterBFS())["nodes"])
