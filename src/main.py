from mixers import graph_from_tx, IterBFS, IterDPS
from render_pyvis import render

def main():
    txid = input("TXID : ").strip()
    if not txid:
        print("Erreur : Aucun identifiant de transaction saisi.")
        txid = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'

    try:
        depth = 4
        graph = graph_from_tx(txid, depth, IterDPS())
        # Le nom du html généré est raltif à la transaction et à la profondeur du graphe
        dst =   f"../html/graph_{txid[:5]}_{depth}.html"
        render(graph, dst)
        print(f"Le graphe a été généré et affiché dans {dst}.")
    except Exception as e:
        print(f"Erreur lors de la génération du graphe : {e}")

if __name__ == "__main__":
    main()