import sys
import requests

BASE_URL = "https://api.blockchain.info/haskoin-store/btc"

def fetch_transaction(txid):
    url = f"{BASE_URL}/transaction/{txid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def build_graph_from_transaction(txid, depth):
    graph = { "nodes": [], "edges": [] }

    cpt = 0
    stack = [txid]

    while cpt < depth and len(stack)>0 :

        txid = stack.pop()
        tx_data = fetch_transaction(txid)
        # ...

        n = { "id": tx_data['txid'],
              "label": f"TX: {tx_data['txid'][:8]}...",
              "type": "transaction" }

        for nd in graph["nodes"]:
            if nd["id"] == txid:
                print(f'DAG {txid}')
        
        graph["nodes"].append(n)

        for inp in tx_data['inputs']:
            addr = inp['address']
            if not inp['coinbase']:
                graph["nodes"].append({
                    "id": addr,
                    "label": f"A: {addr[:5]}...",
                    "type": "address"
                })
                graph["edges"].append({
                    "from": addr,
                    "to": tx_data['txid'],
                    "label": f"{inp['value'] / 100_000_000:.4f} BTC",
                    "input": True,
                    # Pour différencier différent inputs de la même personne.
                    #"input_id": f"{addr}{inp['txid']}{inp['output']}" 
                })

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
                    graph["edges"].append({ "from": tx_data['txid'],
                                            "to": addr,
                                            "label": f"{out['value'] / 100_000_000:.8f} BTC",
                                            "input": False})
                    stack.append(out["spender"]["txid"])
        cpt = cpt + 1

    return graph

if __name__ == "__main__":
    tx = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'
    print(build_graph_from_transaction(tx,1))