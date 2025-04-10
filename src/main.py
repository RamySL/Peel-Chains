from mixers import graph_from_depth,graph_from_nb_nodes, IterBFS, IterDPS, IterPriority
from render_pyvis import render
from render_interactive import render_interactive_with_click_only as render




def main():
    txid = input("TXID : ").strip()
    if not txid:
        print("Erreur : Aucun identifiant de transaction saisi.")
        txid = '87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108'
    # si vous voulez générer en fonction de profondeur mettez True sinon
    by_depth = False
    if by_depth:
        depth = 3
        graph = graph_from_depth(txid, depth, IterDPS())
        # Le nom du html généré est raltif à la transaction et à la profondeur du graphe
        dst =   f"../html/graph_depth_{depth}_{txid[:5]}.html"
        render(graph, dst)
        print(f"Le graphe a été généré et affiché dans {dst}.")

    else:
        n = 3
        iter = IterBFS()
        graph = graph_from_nb_nodes(txid, n, iter)
        # Le nom du html généré est raltif à la transaction et à la profondeur du graphe
        dst =   f"../html/graph_nb_{n}_{iter}_{txid[:5]}.html"
        render(graph, dst)
        print(f"Le graphe a été généré et affiché dans {dst}.")
        



if __name__ == "__main__":
    main()