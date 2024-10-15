import networkx as nx
import matplotlib.pyplot as plt
import nodelist

# Create a graph
G = nx.Graph()

# Assign real-world coordinates for each node (e.g., from a floorplan)
node_positions = nodelist.nodes

# Add edges with distances (weights)
edges_with_distances = []

for node, connections in nodelist.connections_list:
    for connection in connections:
        if isinstance(connection, tuple):  # Check if it's a tuple (node, weight)
            edges_with_distances.append((node, connection[0], connection[1]))

G.add_weighted_edges_from(edges_with_distances)

# Draw the graph using the real-world positions
plt.figure(figsize=(10, 10))
nx.draw_networkx(G, pos=node_positions, with_labels=True, node_color='skyblue', node_size=500, font_size=10, font_weight='bold', edge_color='gray')

# Draw the edge labels (distances)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos=node_positions, edge_labels=edge_labels)

# Display the graph
plt.show()
