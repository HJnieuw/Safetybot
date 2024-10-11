import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Add edges with distances (weights)
edges_with_distances = [
    (0, 1), (0, 5), (0, 4), 
    (1, 2), 
    (2, 3), 
    (3, 4), 
    (4, 5)
]
G.add_weighted_edges_from(edges_with_distances)

# Assign real-world coordinates for each node (e.g., from a floorplan)
node_positions = {
    0:(630.064973,955.012783),
    1:(592.017066,857.289924),
    2:(592.017066,828.95015),
    3:(772.034676,705.314416),
    4:(874.371376,633.788766),
    5:(1406.389376,698.344388)
}

# Draw the graph using the real-world positions
plt.figure(figsize=(10, 10))
nx.draw_networkx(G, pos=node_positions, with_labels=True, node_color='skyblue', node_size=500, font_size=10, font_weight='bold', edge_color='gray')

# Draw the edge labels (distances)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos=node_positions, edge_labels=edge_labels)

# Display the graph
plt.show()
