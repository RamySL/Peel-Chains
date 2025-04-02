from mixers import graph_from_tx, IterBFS, IterDPS
from render_pyvis import render

def main():
    #txid = input("TXID : ").strip()
    txid = None
    if not txid:
        print("Erreur : Aucun identifiant de transaction saisi.")
        txid = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'

    try:
        depth = 4
        graph = graph_from_tx(txid, depth, IterDPS())
        dst =   f"../html/graph{depth}.html"
        render(graph, dst)
        print(f"Le graphe a été généré et affiché dans {dst}.")
    except Exception as e:
        print(f"Erreur lors de la génération du graphe : {e}")

if __name__ == "__main__":
    main()