from pyvis.network import Network
from mixers import *
import time
import json
import os

net = Network(notebook=True, directed=True, height="100vh", width="100%")
TAGS_RANSOME = None

with open('../json/ransom_tags.json', 'r') as file:
    TAGS_RANSOME = json.load(file)

# Couleurs des noeuds
DEFAULT_ADDR = '#0000ff'
RANSOME_ADDR = "#ff0000"
EXCHANGE_ADDR = "#000000"
DEFAULT_TX = "#00ffbf"
FIRST_TX = "#c002fa"
DAG_TX = "#ff0000"

##
first = True # pour colorer diff la premiere tx

def init():
    global net
    net = Network(notebook=True, directed=True, height="100vh", width="100%")
"""
Attend un graphe sous forme de dictionnaire avec comme clés : nodes et edges.
Elle est Hardcode avec la structure dans le fichier ./mixers.py
"""
def render(graph, dst:str):
    init()

    for _,_,e in graph.edges(data=True):
        e = e["meta"]
        from_ = e['from']
        to_ = e['to']
        if (e["input"]):
            #addr
            net.add_node(from_, label=" ", color=color_addr(e["tags"], e["exchange"]), title=format_infos(e['from'], e["tags"]))
            #tx
            net.add_node(to_, label=" ", color=color_tx(e["DAG"]), shape='square', title=format_infos(to_))

            net.add_edge(from_, to_, label=e['label'], color="#000000") 
        else:
            #tx
            net.add_node(from_, label=" ", color=color_tx(e["DAG"]), shape='square', title=format_infos(from_))
            #addr
            net.add_node(to_, label=" ", color=color_addr(e["tags"], e["exchange"]), title=format_infos(to_, e["tags"]))

            net.add_edge(from_, to_, label=e['label'])

    net.show(dst)
    inject_flask_interactive_script(dst)


"""
Donne une couleur pour colorier le noeud avec selon les tags de son adresse
"""
def color_addr(tags, exch):
    if exch:
        return EXCHANGE_ADDR

    for tag in tags:
        if tag in TAGS_RANSOME:
            return RANSOME_ADDR

    return DEFAULT_ADDR

def color_tx(dag):
    global first
    if first:
        first = False
        return FIRST_TX
    if dag:
        return DAG_TX

    return DEFAULT_TX

"""
Retoune les information sur le noeud pour les afficher dans le graphe
"""
def format_infos(id, tags=[]):
    return f"id/addr: {id} \n tags:{tags} "

def inject_flask_interactive_script(dst: str):
    js_script = """
    <script type="text/javascript">
    async function fetchAncestors(nodeId) {
        const response = await fetch("http://127.0.0.1:5000/get_parents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ node_id: nodeId })
        });

        const data = await response.json();
        return data.nodes;
    }

    network.on("click", async function (params) {
        if (params.nodes.length > 0) {
            const clickedNode = params.nodes[0];
            console.log("Node clicked:", clickedNode);

            const visibleNodes = await fetchAncestors(clickedNode);

            // Mettre les noeuds non inclus en gris
            nodes.get().forEach((node) => {
                const keep = visibleNodes.includes(node.id);
                nodes.update({ id: node.id, color: keep ? "#00FF00" : "#d3d3d3" });
            });

            edges.get().forEach((edge) => {
                const keep = visibleNodes.includes(edge.from) && visibleNodes.includes(edge.to);
                edges.update({ id: edge.id, color: keep ? "#0000" : "#d3d3d3" });
            });
        }
    });
    </script>
    """

    if not os.path.exists(dst):
        print(f"Erreur : le fichier {dst} n'existe pas.")
        return

    with open(dst, "r", encoding="utf-8") as file:
        html = file.read()

    if "</body>" in html:
        html = html.replace("</body>", js_script + "\n</body>")

    with open(dst, "w", encoding="utf-8") as file:
        file.write(html)


