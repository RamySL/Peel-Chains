
from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import json

graph = None
TX_SRC = None
app = Flask(__name__)
CORS(app)

@app.route("/get_parents", methods=["POST"])
def get_parents_route():
    global graph, TX_SRC
    data = request.json
    node_id = data.get("node_id")
    path_root = nx.shortest_path(graph,TX_SRC, node_id)
    return jsonify({"nodes": path_root})

'''
Quand le graph est généré, on initialise le graph du serveur comme ça il pourra calculé dessus selon les rêquetes
'''
@app.route("/set_graph", methods = ["POST"])
def set_graph():
    global graph, TX_SRC
    data = request.json
    if not data or "graph" not in data or "tx_src" not in data:
        return jsonify({"error": "Invalid data, 'graph' key is missing"}), 400

    try:
        graph = nx.node_link_graph(data["graph"])
        TX_SRC = data["tx_src"]
        return jsonify({"message": "Graph successfully set"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to set graph: {str(e)}"}), 500

def lunch():
    app.run(debug=True)

if __name__ == "__main__":
    lunch()


    
