from mixers import build_graph_from_transaction
from render_pyvis import render

def main():
    txid = input("TXID : ").strip()
    if not txid:
        print("Erreur : Aucun identifiant de transaction saisi.")
        txid = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'

    try:
        depth = 2
        graph = build_graph_from_transaction(txid, depth)
        render(graph)
        print("Le graphe a été généré et affiché dans 'graph.html'.")
    except Exception as e:
        print(f"Erreur lors de la génération du graphe : {e}")

if __name__ == "__main__":
    main()