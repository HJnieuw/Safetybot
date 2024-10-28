
import cv2
import matplotlib.pyplot as plt
import math

def euclidean_distance(node1, node2):
    x1, y1 = node1
    x2, y2 = node2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def update_connections_with_distances(nodes, connections_list):
    updated_connections = []
    for node_id, connections in connections_list:
        updated_node_connections = []
        for conn in connections:
            connected_node_id = conn[0]
            distance = euclidean_distance(nodes[node_id], nodes[connected_node_id])
            updated_node_connections.append((connected_node_id, distance))
        updated_connections.append((node_id, updated_node_connections))
    return updated_connections

def show_nodes_and_connections(image_path, nodes, connections_list):
    # Load the image
    img = cv2.imread(image_path)

    # Define colors and parameters
    node_color = (0, 0, 255)  # Red color for nodes
    connection_color = (255, 0, 255)  # Green color for connections
    node_radius = 10
    connection_thickness = 2

    # Draw nodes
    for node_id, (x, y) in nodes.items():
        cv2.circle(img, (int(x), int(y)), node_radius, node_color, -1)  # Draw filled circle for each node
        cv2.putText(img, str(node_id), (int(x)-10, int(y)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Draw connections
    for node_id, connections in connections_list:
        for conn in connections:
            connected_node_id = conn[0]
            x1, y1 = nodes[node_id]
            x2, y2 = nodes[connected_node_id]
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), connection_color, connection_thickness)

    # Convert the image from BGR (OpenCV format) to RGB (Matplotlib format)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Display the image with Matplotlib
    plt.figure(figsize=(10, 10))
    plt.imshow(img_rgb)
    plt.axis('off')  # Turn off axis numbers and ticks
    plt.show()


# Example usage
if __name__ == "__main__":
    # Nodes and connections_list as you provided earlier
    nodes = {}

    connections_list = []

    # Update the connections list with the calculated distances
    updated_connections_list = update_connections_with_distances(nodes, connections_list)

    print("updated_connections = [")
    for node_id, connections in updated_connections_list:
        connections_str = ", ".join([f"({conn_id}, {int(distance)})" for conn_id, distance in connections])
        print(f"    ({node_id}, [{connections_str}]),")
    print("]")

    # Show the nodes and their connections on the image
    image_path = 'construction_site_bk.jpg'
    show_nodes_and_connections(image_path, nodes, updated_connections_list)