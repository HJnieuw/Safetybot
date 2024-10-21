import networkx as nx
import matplotlib.pyplot as plt
import BIM_mockup as BIM_mockup

# Create a graph
G = nx.Graph()

# Add nodes
for node_id in BIM_mockup.nodes:
    G.add_node(node_id)

# Add connections (ignore missing weights)
for node, connections in BIM_mockup.connections_list:
    for conn in connections:
        if len(conn) > 1:  # Ignore connections with missing weights
            target_node, weight = conn
            G.add_edge(node, target_node, weight=weight)

''''


# Draw the graph
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G)  # Position nodes using spring layout (ignores real coordinates)

# Draw nodes and edges
nx.draw_networkx_nodes(G, pos, node_size=300)
nx.draw_networkx_edges(G, pos, alpha=0.5)
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f'{d["weight"]}' for u, v, d in G.edges(data=True)})

plt.title("Graph Representation of Nodes and Connections")
plt.axis('off')
plt.show()

'''''

# Define the source and target nodes
source_node = 5  
target_node = 0  
shortest_path = nx.shortest_path(G, source=source_node, target=target_node, weight='weight')
print(shortest_path)


