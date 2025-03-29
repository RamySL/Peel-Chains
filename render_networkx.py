import networkx as nx
import matplotlib.pyplot as plt
from mixers import *

#reset_graph()
#build_graph_from_transaction('87c6dffb5e103e24295a134d2449dccf15ac7a6147f19f2a39731cf121668108', 3)
G = nx.MultiDiGraph()
print (len(graph['edges']))
for e in graph['edges']:
    #print(e)
    if (e["tx_to_out"]):
        G.add_edge("tx:"+e['from'][:10], "addr:"+e['to'][:10], amount=e['label'])
    else:
        G.add_edge("addr:"+e['from'][:10], "tx:"+e['to'][:10], amount=e['label'])

for u, v, data in G.edges(data=True):
    print(f"{u} -> {v}, amount: {data['amount']}")



plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G)  
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", edge_color="gray")
edge_labels = {(u, v): f"{d['amount']}" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

plt.show()