from mixers import build_graph_from_transaction
from render_pyvis import render

def main():
    txid = input("TXID : ").strip()
    if not txid:
        print("Erreur : Aucun identifiant de transaction saisi.")
        return

    try:
        depth = 3 
        graph = build_graph_from_transaction(txid, depth)
        render(graph)
        print("Le graphe a été généré et affiché dans 'graph.html'.")
    except Exception as e:
        print(f"Erreur lors de la génération du graphe : {e}")

if __name__ == "__main__":
    main()