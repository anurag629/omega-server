from manim import *

class NeuralNetworkScene(Scene):
    def construct(self):
        # Define some constants for network structure and appearance
        NUM_LAYERS = 3
        NEURONS_PER_LAYER = [3, 5, 3] # Number of neurons in each layer
        NODE_RADIUS = 0.2
        LAYER_SPACING = 2.5
        NODE_COLOR = BLUE
        EDGE_COLOR = GRAY
        TEXT_COLOR = WHITE

        # Create a VGroup to hold the entire network
        neural_network = VGroup()

        # Create layers of nodes
        layers = []
        for i in range(NUM_LAYERS):
            layer = VGroup()
            for j in range(NEURONS_PER_LAYER[i]):
                node = Circle(radius=NODE_RADIUS, color=NODE_COLOR, fill_opacity=1)
                layer.add(node)
            layer.arrange(DOWN, buff=0.7)
            layers.append(layer)

        # Arrange layers horizontally
        VGroup(*layers).arrange(RIGHT, buff=LAYER_SPACING)
        neural_network.add(*layers) # Add layers to the main VGroup

        # Create edges connecting the nodes
        edges = VGroup()
        for i in range(NUM_LAYERS - 1):
            for node1 in layers[i]:
                for node2 in layers[i+1]:
                    edge = Line(node1.get_center(), node2.get_center(), color=EDGE_COLOR, stroke_width=2)
                    edges.add(edge)
        neural_network.add(edges, layers[0], layers[1], layers[2]) # Ensure edges are behind nodes

        # Add labels for the layers (Input, Hidden, Output)
        input_label = Text("Input", color=TEXT_COLOR).next_to(layers[0], DOWN)
        hidden_label = Text("Hidden", color=TEXT_COLOR).next_to(layers[1], DOWN)
        output_label = Text("Output", color=TEXT_COLOR).next_to(layers[2], DOWN)

        # Animation: Create the network layer by layer
        self.play(Create(layers[0]), Write(input_label))
        self.wait(0.5)
        self.play(Create(layers[1]), Write(hidden_label))
        self.wait(0.5)
        self.play(Create(layers[2]), Write(output_label))
        self.wait(0.5)

        # Animation: Connect the nodes with edges
        self.play(Create(edges))
        self.wait(1)

        # Add a title
        title = Text("Neural Network", color=TEXT_COLOR).to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        # Highlight a path through the network
        input_node = layers[0][0]
        hidden_node = layers[1][2]
        output_node = layers[2][1]

        path_edge1 = Line(input_node.get_center(), hidden_node.get_center(), color=YELLOW, stroke_width=5)
        path_edge2 = Line(hidden_node.get_center(), output_node.get_center(), color=YELLOW, stroke_width=5)

        self.play(Create(path_edge1))
        self.wait(0.5)
        self.play(Create(path_edge2))
        self.wait(1)

        # Clean up the highlighted path
        self.play(FadeOut(path_edge1, path_edge2))
        self.wait(1)

        # Fade out everything
        self.play(FadeOut(neural_network, input_label, hidden_label, output_label, title))
        self.wait(1)