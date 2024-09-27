import os.path

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.colors as mcolors


def plot_graph(hierarchy, results_dir="results", results_prefix=""):
    pos = graphviz_layout(hierarchy, prog='dot')

    # Determine figure size based on nodes and edges
    num_root_nodes = sum(1 for node in hierarchy.nodes() if hierarchy.in_degree(node) == 0)
    max_in_degree = max(hierarchy.in_degree(node) for node in hierarchy.nodes())

    fig_width = max(10, int(num_root_nodes * 1.2))
    node_size = (fig_width / num_root_nodes) * 500
    fig_height = max(5, node_size * max_in_degree / 120)

    plt.figure(figsize=(fig_width, fig_height))

    # Determine node styles
    node_styles = {}
    for node in hierarchy.nodes():
        in_degree = hierarchy.in_degree(node)
        tests = node.tests

        if len(tests) == 0 and in_degree == 0:
            node_styles[node] = 'dotted'
        elif in_degree == 0:
            node_styles[node] = 'double'
        else:
            node_styles[node] = 'solid'

    # Draw nodes
    for node, style in tqdm(node_styles.items(), desc="Drawing nodes"):
        if style == 'double':
            nx.draw_networkx_nodes(hierarchy, pos, nodelist=[node], node_color='lightblue', node_size=node_size,
                                   edgecolors='black', linewidths=1)
            nx.draw_networkx_nodes(hierarchy, pos, nodelist=[node], node_color='none', node_size=node_size * 1.1,
                                   edgecolors='green', linewidths=1)
        elif style == 'dotted':
            nx.draw_networkx_nodes(hierarchy, pos, nodelist=[node], node_color='lightyellow', node_size=node_size,
                                   edgecolors='black', linewidths=1)
        else:
            nx.draw_networkx_nodes(hierarchy, pos, nodelist=[node], node_color='lightblue', node_size=node_size,
                                   edgecolors='black', linewidths=1)

    # Assign unique colors to edges based on target node
    edge_colors = {}
    available_colors = list(mcolors.CSS4_COLORS.keys())  # Use CSS4 named colors
    color_idx = 0

    for target_node in hierarchy.nodes():
        incoming_edges = hierarchy.in_edges(target_node)
        if incoming_edges:
            color = available_colors[color_idx % len(available_colors)]
            color_idx += 1
            for edge in incoming_edges:
                edge_colors[edge] = color

    # Draw edges with assigned colors
    for edge, color in edge_colors.items():
        nx.draw_networkx_edges(
            hierarchy, pos,
            edgelist=[edge],
            arrowstyle='-|>',
            arrowsize=node_size / 40,
            edge_color=color,
            connectionstyle='arc3,rad=0.1',
            node_size=node_size,
            min_source_margin=0,
            min_target_margin=node_size / 100
        )

    # Draw labels
    labels = {node: node.name for node in hierarchy.nodes()}
    nx.draw_networkx_labels(hierarchy, pos, labels, font_size=node_size / 80, font_color='black')

    plt.title("Mutation Subsumption Graph", fontsize=min(20, node_size / 20))
    plt.axis('off')

    # Set plot limits and margins
    x_values, y_values = zip(*pos.values())
    padding = min(20, int(node_size))
    plt.xlim(min(x_values) - padding, max(x_values) + padding)
    plt.ylim(min(y_values) - padding, max(y_values) + padding)

    # Save plot to a file
    print("Plotting...")
    plt.savefig(os.path.join(results_dir, f"{results_prefix}_mutation_subsumption_graph.png"))
    plt.show()
