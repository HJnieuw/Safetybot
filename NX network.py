import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Add edges between the nodes as described
edges = [(0, 1), (0, 5), (0, 4), (1, 2), (2, 3), (3, 4), (4, 5)]
G.add_edges_from(edges)

# Draw the graph
pos = nx.spring_layout(G)  # Position the nodes for a better layout
plt.figure(figsize=(6, 6))
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=12, font_weight='bold', edge_color='gray')
plt.title('NX Network Graph')
plt.show()
