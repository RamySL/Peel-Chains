
from render_pyvis import render
import os

def render_interactive_with_parent_query(graph: dict, dst: str):
    # Génère le graphe normalement
    render(graph, dst)
    inject_flask_interactive_script(dst)

def inject_flask_interactive_script(dst: str):
    js_script = """
    <script type="text/javascript">
    async function fetchAncestors(nodeId) {
        const response = await fetch("http://127.0.0.1:5000/get_parents", {
            method: "POST
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
                edges.update({ id: edge.id, color: keep ? "#000000" : "#d3d3d3" });
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
