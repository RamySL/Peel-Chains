
from flask import Flask, request, jsonify
import networkx as nx
import json

app = Flask(__name__)

# Fonction utilitaire : charger un graphe orienté depuis un dictionnaire de Pyvis
def load_graph_from_data(graph_dict):
    G = nx.DiGraph()
    for edge in graph_dict["edges"]:
        G.add_edge(edge["from"], edge["to"])
    return G

# Charger le graphe depuis edges.json
with open("edges.json", "r") as f:
    graph_dict = json.load(f)
    G = load_graph_from_data(graph_dict)

@app.route("/get_parents", methods=["POST"])
def get_parents_route():
    data = request.json
    node_id = data.get("node_id")

    if not node_id or node_id not in G.nodes:
        return jsonify({"nodes": []})

    ancestors = list(nx.ancestors(G, node_id))
    ancestors.append(node_id)  # inclure aussi le noeud cliqué
    return jsonify({"nodes": ancestors})

if __name__ == "__main__":
    print("Serveur Flask lancé sur http://127.0.0.1:5000")
    app.run(debug=True)
