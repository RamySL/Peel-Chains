from pyvis.network import Network
from mixers import *
from scrapp_arkham import *
import time
from collect_tags import *

net = Network(notebook=True)

for e in graph['edges']:
    #print(e)
    if (e["tx_to_out"]):
        from_ = e['from']
        to_ = e['to'] 

        #tags = scrapp_tags(e['to'])
        tags=[]
        if tags :
            for tag in tags:
                if tag in suspicious_tags : 
                    print("!!!!!!!!! : " + tag)
        time.sleep(2)

        net.add_node(from_,label="", color="red", shape="rectangle", title="Transaction : " + e['from'][:10])
        net.add_node(to_, label="", title="Transaction")
        net.add_edge(from_, to_)

        
    else:
        from_ = e['from']
        to_ = e['to']
        tags=[]
        #tags = scrapp_tags(e['from'])
        if tags :
            for tag in tags:
                if tag in suspicious_tags : 
                    print("!!!!!!!!! : " + tag)
                
        time.sleep(2)

        #net.add_node(from_)
        net.add_node(from_,label="a", color="red", size=30, shape="triangle", title="Première adresse Bitcoin")
        net.add_node(to_)
        net.add_edge(from_, to_)

   
# Plusieurs options peuvent être
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
net.show("graph.html")

