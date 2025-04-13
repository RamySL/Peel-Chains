from mixers import graph_from_depth,graph_from_nb_nodes, IterBFS, IterDPS, IterPriority
import render_graph as rg
import requests
import networkx as nx
def main():
    txid = input("TXID : ").strip()
    if not txid:
        print("Erreur : Aucun identifiant de transaction saisi.")
        txid = 'e102fa789cd29ae5c249d17ef167a24a5c2c54f593aad8083a29d1233a3656b7' #35 btc
        #txid = "c04f5862d5d9cd90a66470711e203d4b5dd87ddf489d67192a6577f81eaa7bf3" #dag + exch
        #txid = "040a5996a3e0b2547d9301b225b4c246a06d8fdec67cfd15197a161fafa69811"
    # si vous voulez générer en fonction de profondeur mettez True sinon
    by_depth = False
    graph = None
    if by_depth:
        depth = 3
        graph = graph_from_depth(txid, depth, IterDPS())
        # Le nom du html généré est raltif à la transaction et à la profondeur du graphe
        dst =   f"../html/graph_depth_{depth}_{txid[:5]}.html"
        rg.render(graph, dst)
        print(f"Le graphe a été généré et affiché dans {dst}.")

    else:
        n = 5
        iter = IterPriority(1)
        graph = graph_from_nb_nodes(txid, n, iter)
        # Le nom du html généré est raltif à la transaction et à la profondeur du graphe
        dst =   f"../html/graph_nb_{n}_{iter}_{txid[:5]}.html"
        rg.render(graph, dst)
        print(f"Le graphe a été généré et affiché dans {dst}.")
    
    send_init_to_server(graph, txid)
        

def send_init_to_server(graph, tx_src):
    url = "http://127.0.0.1:5000/set_graph"  
    try:
        # sérialisation en json du graph
        graph_data = nx.node_link_data(graph)
        response = requests.post(url, json={"graph": graph_data, "tx_src":tx_src})
        if response.status_code == 200:
            print("Graphe envoyé avec succès au serveur.")
        else:
            print(f"Erreur lors de l'envoi du graphe : {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'envoi du graphe : {e}")

if __name__ == "__main__":
    main()