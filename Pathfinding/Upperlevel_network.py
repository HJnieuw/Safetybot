import networkx as nx
import matplotlib.pyplot as plt
import BIM_mockup as BIM_mockup

class GraphAnalyzer:
    def __init__(self, nodes, connections):
        """Initialize the graph with nodes and connections."""
        self.G = nx.Graph()
        self.add_nodes(nodes)
        self.add_connections(connections)

    def add_nodes(self, nodes):
        """Add nodes to the graph."""
        for node_id in nodes:
            self.G.add_node(node_id)

    def add_connections(self, connections):
        """Add connections (edges) to the graph."""
        for node, conn_list in connections:
            for conn in conn_list:
                if len(conn) > 1:  # Ensure connection has both target node and weight
                    target_node, weight = conn
                    self.G.add_edge(node, target_node, weight=weight)

    def find_shortest_path(self, source, target):
        """Find and return the shortest path between two nodes."""
        if nx.has_path(self.G, source, target):
            shortest_path = nx.shortest_path(self.G, source=source, target=target, weight='weight')
            return shortest_path
        else:
            return None

    def visualize_graph(self):
        """Visualize the graph using matplotlib."""
        pos = nx.spring_layout(self.G)  # positions for all nodes
        nx.draw(self.G, pos, with_labels=True, node_color='lightblue', node_size=700, font_size=10, font_color='black')

        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)

        plt.title("Graph Visualization")
        plt.show()

# Example usage (this would be in a separate script)
if __name__ == "__main__":
    # Initialize the GraphAnalyzer with nodes and connections from BIM_mockup
    analyzer = GraphAnalyzer(BIM_mockup.nodes, BIM_mockup.connections_list)

    # Define source and target nodes
    source_node = 1  
    target_node = 5

    # Find the shortest path
    shortest_path = analyzer.find_shortest_path(source_node, target_node)
    if shortest_path:
        print("Shortest path:", shortest_path)
    else:
        print(f"No path exists between {source_node} and {target_node}.")

    # Visualize the graph
    analyzer.visualize_graph()