import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# Check the version of networkx
print(nx.__version__)

# Create the graph
G = nx.Graph()  # Correct capitalization

# Add nodes
G.add_node("Zone_1")
G.add_node("Zone_2")
G.add_node("Zone_3")
G.add_nodes_from(range(16))

# Add edges
G.add_edge("Zone_1", "Zone 3", time=10)
G.add_edge(5, 7)

# Draw the graph with labels
nx.draw(G, with_labels=True)
plt.show()
