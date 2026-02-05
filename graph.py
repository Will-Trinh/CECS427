import networkx as nx
from matplotlib.lines import Line2D
import math
import random
import argparse
from collections import deque
from matplotlib import pyplot as plt

# CECS 427: Assignment 1
# Oanh Tran 029661786
# William Trinh 030650397

# =============================================================================
# Argument Parsing
# =============================================================================

def parse_args():
    '''Parse command-line arguments for the graph analysis program.'''
    p = argparse.ArgumentParser(
        description="Erdos-Renyi Graph Generator and Analyzer"
    )
    #arg input graph file overided
    p.add_argument("--input", type=str, 
                   help="Reads a graph from the given .gml file")
    #args create random graph n, c -> datatypes converted/checked later
    p.add_argument("--create_random_graph", nargs=2, type=float, metavar=("n", "c"),
                   help="Generates a new Erdos-Renyi graph with n nodes and edge probability p = c*ln(n)/n")
    #args a1, a2, a3 etc for multi bfs
    p.add_argument("--multi_BFS", nargs="+", type=str,
                   help="Computes BFS from each starting node, storing all shortest paths")
    p.add_argument("--analyze", action="store_true",
                   help="Performs structural analyses on the graph")
    p.add_argument("--plot", action="store_true",
                   help="Visualizes the graph with highlighted BFS paths and isolated nodes")
    #args output graph gml file
    p.add_argument("--output", type=str,
                   help="Saves the final graph with computed attributes to the specified .gml file")
    return p


# =============================================================================
# File I/O
# =============================================================================

def read_graph_file(file: str):
    '''Read a graph from a .gml file.'''
    return nx.read_gml(file)


def output_graph(G, file: str, bfs_results=None):
    '''Save the graph to a .gml file with enriched node attributes.'''
    if not file.endswith(".gml"):
        file += ".gml"
    
    # Create a copy to add attributes without modifying original
    G_copy = G.copy()
    
    # Add component IDs to nodes
    components = list(nx.connected_components(G_copy))
    for comp_id, component in enumerate(components):
        for node in component:
            G_copy.nodes[node]['component_id'] = comp_id
    
    # Mark isolated nodes
    isolated = set(nx.isolates(G_copy))
    for node in G_copy.nodes():
        G_copy.nodes[node]['is_isolated'] = node in isolated
    
    # Add BFS attributes (distances and parents)
    if bfs_results:
        for source, parent_dict in bfs_results.items():
            # Calculate distances from parent dict
            distances = compute_distances(parent_dict, source)
            for node in G_copy.nodes():
                # Store distance from this BFS source
                dist_key = f'bfs_{source}_distance'
                parent_key = f'bfs_{source}_parent'
                
                if node in distances:
                    G_copy.nodes[node][dist_key] = distances[node]
                    G_copy.nodes[node][parent_key] = str(parent_dict.get(node, "None"))
                else:
                    G_copy.nodes[node][dist_key] = -1  # Unreachable
                    G_copy.nodes[node][parent_key] = "None"
    
    nx.write_gml(G_copy, file)
    print(f"\nGraph saved to {file}")


def compute_distances(parent_dict, source):
    '''Compute distances from source to all reachable nodes using the parent dictionary.'''
    distances = {source: 0}
    for node in parent_dict:
        if node not in distances:
            # Trace back to source
            path = []
            current = node
            while current is not None and current not in distances:
                path.append(current)
                current = parent_dict.get(current)
            
            if current is not None:
                base_dist = distances[current]
                for i, n in enumerate(reversed(path)):
                    distances[n] = base_dist + i + 1
    return distances


# =============================================================================
# Graph Generation - Erdős–Rényi model
# =============================================================================

def generate_graph(n: int, c: float):
    '''Generate a random Erdos-Renyi graph with n nodes and edge probability p = c*ln(n)/n.'''
    G = nx.Graph()
    # Add nodes with string labels "0" to "n-1"
    G.add_nodes_from([str(i) for i in range(n)])
    
    # Probability of edge: p = c * ln(n) / n
    p = (c * math.log(n)) / n

    #add nodes with labels "0" to "n-1"
    # For each node pair, add edge with probability p
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                G.add_edge(str(i), str(j))
    
    return G


# =============================================================================
# Breadth First Search
# =============================================================================

def bfs(graph, start):
    '''Perform breadth-first search from a starting node and return the parent dictionary.'''
    parent = {}
    visited = {start}
    queue = deque([start])
    parent[start] = None
    
    print(f"BFS from {start} - Visited nodes: ", end="")
    visit_order = []
    
    while queue:
        node = queue.popleft()
        visit_order.append(node)
        
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                queue.append(neighbor)
    
    print(", ".join(visit_order))
    return parent


def print_bfs_tree(parent, start):
    '''Print a text-based visualization of the BFS tree.'''
    # Build children dictionary
    children = {}
    for node, par in parent.items():
        children.setdefault(node, [])
        if par is not None:
            children.setdefault(par, []).append(node)
    
    # Sort children for consistent output
    for k in children:
        children[k].sort(key=lambda x: (len(x), x))  # Sort by length then lexicographically
    
    def dfs_print(node, prefix="", is_last=True):
        if prefix == "":
            print("   " + node)
        else:
            print(prefix + ("+-- " if is_last else "+-- ") + node)
        kids = children.get(node, [])
        new_prefix = prefix + ("    " if is_last else "|   ")
        for i, child in enumerate(kids):
            dfs_print(child, new_prefix, i == len(kids) - 1)
    
    print(f"\nBFS Tree from {start}:")
    dfs_print(start)


def draw_bfs_tree(graph, parent, source):
    '''Draw a graphical visualization of the BFS tree using matplotlib.'''
    # Build the BFS tree as a directed graph
    tree = nx.DiGraph()
    tree.add_nodes_from(parent.keys())
    for node, par in parent.items():
        if par is not None:
            tree.add_edge(par, node)
    
    # Calculate levels for hierarchical layout
    distances = compute_distances(parent, source)
    
    # Position nodes by level
    positions = {}
    levels = {}
    for node, dist in distances.items():
        if dist not in levels:
            levels[dist] = []
        levels[dist].append(node)
    
    # Sort nodes at each level for consistent positioning
    for level in levels:
        levels[level].sort(key=lambda x: (len(x), x))
    
    # Assign x,y positions
    for level, nodes in levels.items():
        for i, node in enumerate(nodes):
            x = i - len(nodes) / 2
            y = -level
            positions[node] = (x, y)
    
    # Draw the tree
    plt.figure(figsize=(10, 8))
    plt.title(f"BFS Tree from Node {source}", fontsize=14, fontweight='bold')
    
    nx.draw(tree, positions, 
            with_labels=True, 
            node_color="lightblue",
            node_size=800,
            font_size=10,
            font_weight='bold',
            edge_color='gray',
            arrows=True,
            arrowsize=15)
    
    plt.tight_layout()
    plt.savefig(f"bfs_tree_{source}.png", format="PNG", dpi=300)
    plt.show()


def multi_bfs(G, *start_nodes):
    '''Perform BFS from multiple starting nodes and return all parent dictionaries.'''
    results = {}
    
    for node in start_nodes:
        if node not in G.nodes:
            raise ValueError(f"Node '{node}' does not exist in the graph")
        
        print(f"\n{'='*50}")
        print(f"Running BFS from node {node}")
        print('='*50)
        
        parent = bfs(G, node)
        results[node] = parent
        
        # Print text tree
        print_bfs_tree(parent, node)
        
        # Draw graphical tree
        draw_bfs_tree(G, parent, node)
    
    return results


# =============================================================================
# Graph Analysis
# =============================================================================

def analysis(G):
    '''Perform comprehensive structural analysis on the graph.'''
    edges = G.number_of_edges()
    nodes = G.number_of_nodes()
    
    print("\n" + "="*50)
    print(" GRAPH ANALYSIS ".center(50, "="))
    print("="*50)
    
    print(f"\nBasic Statistics:")
    print(f"  - Nodes: {nodes}")
    print(f"  - Edges: {edges}")
    
    # Connected Components - count ALL components including isolated nodes
    components = list(nx.connected_components(G))
    print(f"\n--- Connected Components ---")
    print(f"Total Connected Components: {len(components)}")
    
    for i, comp in enumerate(components):
        if len(comp) > 1:
            print(f"  Component {i+1} (size {len(comp)}): {sorted(comp, key=lambda x: (len(x), x))}")
        else:
            print(f"  Component {i+1} (size 1): {list(comp)} [isolated]")
    
    # Cycle Detection
    cycles = nx.cycle_basis(G)
    print(f"\n--- Cycle Detection ---")
    if cycles:
        print(f"Cycles found: {len(cycles)}")
        for i, cycle in enumerate(cycles, 1):
            cycle_str = ' -> '.join(cycle) + ' -> ' + cycle[0]
            print(f"  Cycle {i}: {cycle_str}")
    else:
        print("No cycles found - graph is acyclic (tree/forest)")
    
    # Isolated Nodes
    isolated = list(nx.isolates(G))
    print(f"\n--- Isolated Nodes ---")
    if isolated:
        print(f"Isolated nodes ({len(isolated)}): {sorted(isolated, key=lambda x: (len(x), x))}")
    else:
        print("No isolated nodes")
    
    # Graph Density
    density = nx.density(G)
    print(f"\n--- Graph Density ---")
    print(f"Density: {density:.4f}")
    print(f"  (0 = no edges, 1 = fully connected)")
    
    # Average Shortest Path Length
    print(f"\n--- Average Shortest Path Length ---")
    if nx.is_connected(G):
        avg_path = nx.average_shortest_path_length(G)
        print(f"Average shortest path length: {avg_path:.4f}")
    else:
        print("Graph is not connected; computing for largest component...")
        largest_cc = max(components, key=len)
        subgraph = G.subgraph(largest_cc)
        if len(largest_cc) > 1:
            avg_path = nx.average_shortest_path_length(subgraph)
            print(f"Average shortest path length (largest component): {avg_path:.4f}")
        else:
            print("Largest component has only 1 node; path length undefined")
    
    print("\n" + "="*50)


# =============================================================================
# Visualization
# =============================================================================

def plot(G, bfs_results=None):
    '''Visualize the graph with highlighted BFS paths and distinct isolated node styling.'''
    plt.figure(figsize=(12, 10))
    
    # Get layout
    pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
    
    # Identify isolated nodes
    isolated_nodes = list(nx.isolates(G))
    normal_nodes = [node for node in G.nodes() if node not in isolated_nodes]
    
    # Draw all edges first (gray, thin)
    nx.draw_networkx_edges(G, pos, edge_color="#CCCCCC", width=1, alpha=0.5)
    
    # Highlight BFS paths if provided
    bfs_colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta']
    legend_elements = []
    
    if bfs_results:
        for idx, (source, parent_dict) in enumerate(bfs_results.items()):
            color = bfs_colors[idx % len(bfs_colors)]
            
            # Get all edges in the BFS tree
            bfs_edges = []
            for node, par in parent_dict.items():
                if par is not None:
                    bfs_edges.append((par, node))
            
            # Draw BFS edges with distinct color
            nx.draw_networkx_edges(G, pos, edgelist=bfs_edges, 
                                   edge_color=color, width=2.5, alpha=0.8)
            
            # Add to legend
            legend_elements.append(
                Line2D([0], [0], color=color, linewidth=2.5, 
                       label=f'BFS paths from {source}')
            )
    
    # Draw normal nodes
    if normal_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes,
                               node_color="#95B18E", node_size=600,
                               edgecolors='darkgreen', linewidths=1.5)
    
    # Draw isolated nodes with distinct styling
    if isolated_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=isolated_nodes,
                               node_color="#E57373", node_size=600,
                               edgecolors='darkred', linewidths=2,
                               node_shape='s')  # Square shape for isolated
    
    # Draw BFS source nodes with special highlighting
    if bfs_results:
        source_nodes = list(bfs_results.keys())
        nx.draw_networkx_nodes(G, pos, nodelist=source_nodes,
                               node_color="#FFD700", node_size=800,
                               edgecolors='black', linewidths=2)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    
    # Build legend
    legend_elements.extend([
        Line2D([0], [0], marker='o', color='w', label='Normal Node',
               markerfacecolor="#95B18E", markeredgecolor='darkgreen',
               markersize=12, markeredgewidth=1.5),
        Line2D([0], [0], marker='s', color='w', label='Isolated Node',
               markerfacecolor="#E57373", markeredgecolor='darkred',
               markersize=12, markeredgewidth=2),
    ])
    
    if bfs_results:
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', label='BFS Source Node',
                   markerfacecolor="#FFD700", markeredgecolor='black',
                   markersize=12, markeredgewidth=2)
        )
    
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    # Title
    title = "Graph Visualization"
    if bfs_results:
        sources = ', '.join(bfs_results.keys())
        title += f"\nBFS Sources: {sources}"
    plt.title(title, fontsize=14, fontweight='bold')
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("graph_visualization.png", format="PNG", dpi=300, bbox_inches='tight')
    print("\nGraph visualization saved to graph_visualization.png")
    plt.show()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    '''Main entry point for the graph analysis program.'''
    parser = parse_args()
    args = parser.parse_args()
    
    G = None
    bfs_results = None
    
    # Handle graph creation/loading
    if args.create_random_graph:
        try:
            n = int(args.create_random_graph[0])
            c = float(args.create_random_graph[1])
        except ValueError:
            parser.error("--create_random_graph: n must be an integer, c must be a number")
        
        if n <= 0 or c <= 0:
            parser.error("--create_random_graph: n and c must be positive")
        
        print(f"Generating Erdos-Renyi random graph with n={n}, c={c}")
        print(f"Edge probability p = c*ln(n)/n = {(c * math.log(n)) / n:.6f}")
        G = generate_graph(n, c)
        
        print(f"\nGraph created:")
        print(f"  Nodes: {G.number_of_nodes()}")
        print(f"  Edges: {G.number_of_edges()}")
        
    elif args.input:
        try:
            print(f"Loading graph from {args.input}...")
            G = read_graph_file(args.input)
            print(f"Graph loaded successfully:")
            print(f"  Nodes: {G.number_of_nodes()}")
            print(f"  Edges: {G.number_of_edges()}")
        except FileNotFoundError:
            print(f"Error: Input file not found: {args.input}")
            return
        except nx.NetworkXError as e:
            print(f"Error: Malformed input file: {args.input}")
            print(f"  Details: {e}")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        parser.error("Either --input or --create_random_graph must be provided")
    
    # Handle multi-BFS
    if args.multi_BFS:
        try:
            bfs_results = multi_bfs(G, *args.multi_BFS)
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Available nodes: {sorted(G.nodes(), key=lambda x: (len(x), x))}")
            return
    
    # Handle analysis
    if args.analyze:
        analysis(G)
    
    # Handle plotting
    if args.plot:
        plot(G, bfs_results)
    
    # Handle output
    if args.output:
        output_graph(G, args.output, bfs_results)


if __name__ == "__main__":
    main()