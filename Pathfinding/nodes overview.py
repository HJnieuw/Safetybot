import networkx as nx
import matplotlib.pyplot as plt

# Define the list of edges
edges = [
    (0, 1), (0, 5), (0, 4),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6), (5, 20),
    (6, 19), (6, 7),
    (7, 8), (7, 19),
    (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14), (8, 15), (8, 16), (8, 17), (8, 18), (8, 19), (8, 20),
    (8, 21), (8, 22), (8, 23), (8, 24), (8, 25), (8, 26), (8, 27),
    (9, 11), (9, 12), (9, 13), (9, 14), (9, 15), (9, 16), (9, 17), (9, 18), (9, 19), (9, 20),
    (9, 21), (9, 22), (9, 23), (9, 24), (9, 25), (9, 26), (9, 27),
    (10, 11), (10, 12), (10, 13), (10, 14), (10, 15), (10, 16), (10, 17), (10, 18), (10, 19),
    (10, 20), (10, 21), (10, 22), (10, 23), (10, 24), (10, 25), (10, 26), (10, 27),
    (11, 13), (11, 14), (11, 15), (11, 16), (11, 17), (11, 18), (11, 19), (11, 20),
    (11, 21), (11, 22), (11, 23), (11, 24), (11, 25), (11, 26), (11, 27),
    (12, 13), (12, 14), (12, 15), (12, 16), (12, 17), (12, 18), (12, 19), (12, 20),
    (12, 21), (12, 22), (12, 23), (12, 24), (12, 25), (12, 26), (12, 27),
    (13, 14), (13, 15), (13, 16), (13, 17), (13, 18), (13, 19), (13, 20),
    (13, 21), (13, 22), (13, 23), (13, 24), (13, 25), (13, 26), (13, 27),
    (14, 16), (14, 17), (14, 18), (14, 19), (14, 20), (14, 21), (14, 22), (14, 23),
    (14, 24), (14, 25), (14, 26), (14, 27),
    (15, 16), (15, 17), (15, 18), (15, 19), (15, 20), (15, 21), (15, 22), (15, 23),
    (15, 24), (15, 25), (15, 26), (15, 27),
    (16, 18), (16, 19), (16, 20), (16, 21), (16, 22), (16, 23), (16, 24), (16, 25),
    (16, 26), (16, 27),
    (17, 18), (17, 19), (17, 20), (17, 21), (17, 22), (17, 23), (17, 24), (17, 25),
    (17, 26), (17, 27),
    (18, 19), (18, 20), (18, 21), (18, 23), (18, 24), (18, 25), (18, 26), (18, 27),
    (19, 20), (19, 21), (19, 22), (19, 23), (19, 24), (19, 25), (19, 26), (19, 27),
    (20, 21), (20, 22), (20, 23), (20, 24), (20, 25), (20, 26), (20, 27),
    (21, 22), (21, 24), (21, 25), (21, 26), (21, 27),
    (22, 23), (22, 24), (22, 25), (22, 26), (22, 27),
    (23, 24), (23, 25), (23, 26), (23, 27),
    (24, 26), (24, 27),
    (25, 26), (25, 27),
    (26, 27), (27, 28), (27, 29),
    (28, 27), (29, 27)
]

# Create a directed graph
G = nx.Graph()

# Add edges to the graph
G.add_edges_from(edges)

# Draw the graph
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G)  # positions for all nodes
nx.draw_networkx_nodes(G, pos, node_size=300)
nx.draw_networkx_edges(G, pos, alpha=0.5)
nx.draw_networkx_labels(G, pos, font_size=10)

# Display the graph
plt.title("Graph Visualization of Nodes and Connections")
plt.axis('off')  # Turn off the axis
plt.show()