import sys
import requests
import json

BASE_URL = "https://api.blockchain.info/haskoin-store/btc"
nb_dags = 0

def fetch_transaction(txid):
    url = f"{BASE_URL}/transaction/{txid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def build_graph_from_transaction(txid, depth, write=False, dst="edges.json"):
    global nb_dags
    graph = { "nodes": [], "edges": [] }

    if write:
        with open(dst, 'w') as file:
            json.dump({"edges": []}, file)

    cpt = 0
    stack = [txid]

    while cpt < depth and len(stack)>0 :

        txid = stack.pop()
        tx_data = fetch_transaction(txid)
        # ...

        n = { "id": tx_data['txid'],
              "label": f"TX: {tx_data['txid'][:8]}...",
              "type": "transaction",
               "DAG": False }

        for nd in graph["nodes"]:
            if nd["id"] == txid:
                print(f'DAG {txid}')
                nb_dags += 1
                n["DAG"] = True
           
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
                    "to": tx_data['txid'],
                    "label": f"{inp['value'] / 100_000_000:.4f} BTC",
                    "input": True,
                    "DAG": n["DAG"]
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
                if out.get("spent") and out.get("spender"):
                    node["expand_txid"] = out["spender"]["txid"]
                    graph["nodes"].append(node)
                    edge = { "from": tx_data['txid'],
                                            "to": addr,
                                            "label": f"{out['value'] / 100_000_000:.8f} BTC",
                                            "input": False,
                                            "DAG": False
                                            }
                    graph["edges"].append(edge)
                    if write:
                        append_to_json_list(dst, "edges", edge)
                    stack.append(out["spender"]["txid"])
        cpt = cpt + 1

    return graph
   
import json

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
    build_graph_from_transaction(tx,3)