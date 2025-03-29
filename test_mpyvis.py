from pyvis.network import Network

net = Network(notebook=True)

net.add_node("0",label=" ", title="Transaction \n whs whs \n dinnndndndn", shape="square")





   
# Plusieurs options peuvent être définies pour l'affichage
net.set_options('''
var options = {
  "edges": {
    "arrows": {
      "to": {
        "enabled": true,
        "scaleFactor": 1
      }
    }
  }
}
''')
net.show("graph_test.html")