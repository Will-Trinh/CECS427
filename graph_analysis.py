import networkx as nx
import math
import random
import argparse
from collections import deque
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.colors import LinearSegmentedColormap



# CECS 427: Assignment 2
# Oanh Tran 029661786
# William Trinh 030650397

# =============================================================================
# Argument Parsing
# =============================================================================

def parse_args():
    p=argparse.ArgumentParser(description="Graph Analysis of Network Structures and Dynamic Network Behaviors")
    #input file
    p.add_argument("--input",type=str,required=True,help="Input .gml graph file")
    #partition
    p.add_argument("--components",type=int,help="Partition graph into n components using Girvan-Newman")
    #export each component
    p.add_argument("--split_output_dir", action="store_true", help="Export each component as separate .gml files")    #plotting visualization
    p.add_argument("--plot",choices=["C", "c","N","n","P","p"],help="Visualization: C=clustering,N=overlap,P=attributes")
    #verify homophilly and whether the graph is balance
    p.add_argument("--verify_homophily",action="store_true",help="Run t-test for homophilly on node attributes")
    p.add_argument("--verify_balanced_graph",action="store_true",help="Check if signed graph is structurally balanced")
    #randomly remove k edges and evaluate changes
    p.add_argument("--simulate_failures",type=int,help="Remove k random edges and analyze network impact")
    #perform random edge failures and report
    p.add_argument("--robustness_check",type=int,help="Run multiple k-edge failure simulations before partitioning")
    #load time series of edge changes in CSV format
    p.add_argument("--temporal_simulation",type=str,help="CSV of edge events to animate graph evolution")
    p.add_argument("--output", nargs="?", const="outputFinal.gml", help="Save final graph to .gml (optional filename)"
)
    return p.parse_args()



# =============================================================================
# File I/O
# =============================================================================

def read_graph_file(file: str):
    '''Read a graph from a .gml file.'''
    return nx.read_gml(file)

def printStats(graph):
    print("-" * 30)
    degrees = dict(graph.degree())
    isolated = list(nx.isolates(graph))
    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    components = list(nx.connected_components(graph))
    isolated = list(nx.isolates(graph))
    print(f"Nodes: {n}")
    print(f"Edges: {m}")
    print(f"Components: {len(components)}")
    print(f"Isolated Nodes: {len(isolated)}")
    for i, comp in enumerate(components, 1):
        print(f"Component {i:>2} | Size: {len(comp):>2} | Nodes: {sorted(comp)}")
    print("-" * 30)
    

#==============================================================================
#Partition graph into n components using Girvan Newman method until n number of components
#find edge with highest betweeness and remove edge from graph
#continue until n connected components
#==============================================================================

def edgeBetweeness(graph):
    return nx.edge_betweenness_centrality(graph)

def partition(graph, n):
    num_components = nx.number_connected_components(graph)
    if num_components > n:
        print(f"Graph already has {num_components} components (> {n}).")
        return graph
    if num_components == n:
        print("Graph already has desired number of components.")
        return graph
    print(f"\n\nUsing Girvan–Newman Method to Partition: Graph Into {n} Components")
    print("-" * 50)
    step = 1
    print("\nGraph Stats Before Partitioning")
    printStats(graph)
    while num_components < n and graph.number_of_edges() > 0:
        print(f"\nStep {step}")
        between = edgeBetweeness(graph)
        edge = max(between, key=between.get)
        print(f"Highest betweenness edge: {edge} (score={between[edge]:.4f})")
        
        graph.remove_edge(*edge)
        print(f"Removed edge: {edge}")
        
        num_components = nx.number_connected_components(graph)
        print(f"Current number of components: {num_components}")
        print(f"Remaining edges: {graph.number_of_edges()}")
        
        components = list(nx.connected_components(graph))
        print(f"Total Components: {len(components)}")
        for i, comp in enumerate(components, 1):
            print(f"Component {i:>2} | Size: {len(comp):>2} | Nodes: {sorted(comp)}")
        step += 1

    print("\nGraph Stats After Partitioning")
    printStats(graph)
    return graph
    

#==============================================================================
#Output graph components and the --output final graph
#==============================================================================
def outputComponents(graph):
    components = list(nx.connected_components(graph))
    for i, nodes in enumerate(components, 1):
        subgraph = graph.subgraph(nodes).copy()
        filename = f"component_{i}.gml"
        nx.write_gml(subgraph, filename)

    print(f"\nExported {len(components)} components as separate .gml files in current folder.")
    
def outputFinal(graph, filename):
    if not filename.endswith(".gml"):
        filename += ".gml"
    nx.write_gml(graph, filename)
    print(f"\nFinal graph saved as: {filename}") 
    
    
#==============================================================================
# Plot
#===============================================================================
def plot(graph, choice):
    if graph.number_of_nodes() == 0:
        print("Graph is empty....")
        return
    pos = nx.spring_layout(graph, seed=42,k = 1.5, iterations=200)
    #----- C --------
    if choice.lower() == 'c':
        print("Plotting clustering coefficient...")
        # Compute cc for each node and dict of degrees
        cc = nx.clustering(graph)
        degree = dict(graph.degree())

        nodeSizes = [300 + cc[n] * 2000 for n in graph.nodes()]
        nodeColors = [degree[n] for n in graph.nodes()]
        fig, ax = plt.subplots(figsize = (10, 8))

        nodes = nx.draw_networkx_nodes(
            graph, pos,
            node_size=nodeSizes, node_color=nodeColors,
            cmap=plt.cm.BuPu, edgecolors = "black",
            ax=ax
        )
        
        nx.draw_networkx_edges(graph, pos, ax=ax)
        nx.draw_networkx_labels(graph, pos, ax=ax)
        cBar = fig.colorbar(nodes, ax=ax, label="Degree")
        cBar.set_ticks(range(min(nodeColors), max(nodeColors) + 1))
        ax.set_title("Clustering Coefficient (size) & Degree (color)", pad = 15)
        ax.set_axis_off()
        plt.show()
        
    #plot N -> thickness of edges by neighborhood overlap, color edges (deg(u)+deg(v))
    #----- N --------
    if choice.lower() == 'n':
        print("Plotting the Neighborhood Overlap... ")
        pos = nx.spring_layout(graph, seed=42,k = 2.0, iterations=200)

        fig, ax = plt.subplots(figsize = (10, 8))
        edgeList = list(graph.edges())
        degree = dict(graph.degree())
        edgeWidth = []
        edgeColors = []
        edgeLabels = {}
        
        for u, v in edgeList:
            neighborO = neighborhoodOverlap(graph, u, v)
            edgeWidth.append(1 + neighborO * 8)
            edgeColors.append(degree[u] + degree[v])
            edgeLabels[(u, v)] = round(neighborO, 2)

        nodes = nx.draw_networkx_nodes(
            graph, pos,
            node_size=600, node_color ="#cfe8ff", edgecolors="black",
            ax=ax
        )
        nx.draw_networkx_edges(
            graph, pos,
            edgelist=edgeList,
            width=edgeWidth, edge_color=edgeColors,
            edge_cmap=plt.cm.tab20, edge_vmin=min(edgeColors),
            ax=ax
        )
        nx.draw_networkx_edge_labels(
            graph, pos,
            edge_labels=edgeLabels, font_size=8,
            ax=ax
        )
        nx.draw_networkx_labels(graph, pos, ax=ax)
        handles = []
        for val in sorted(set(edgeColors)):
            handles.append(
                mpatches.Patch(
                    color=plt.cm.tab20((val - min(edgeColors)) / (max(edgeColors) - min(edgeColors))),
                    label=str(val)
                )
            )
        ax.legend(handles=handles, title="Degree Sum (u+v)")
        ax.set_title("Neighborhood Overlap (width) & Degree Sum (color)")
        ax.set_axis_off()
        plt.show()
        
    #----- P --------
    if choice.lower() == 'p':
        print("Plotting node and edge attributes....")
        fig, ax = plt.subplots(figsize=(10, 8))
        components = list(nx.connected_components(graph))
        cMap = LinearSegmentedColormap.from_list(
            "myGradient", ["#dfd7d0", "#f0dabf", "#e7cfa5", "#deddce", "#f7bca9"]
        )
        # Map node -> component index
        node_to_comp = {}
        for idx, comp in enumerate(components):
            for node in comp:
                node_to_comp[node] = idx
        # Build node colors in the SAME order as graph.nodes()
        n_comp = len(components)
        nodeColors = [
            cMap(node_to_comp[node] / max(1, n_comp - 1))
            for node in graph.nodes()
        ]
        # --- Build edge list once (post-partition) ---
        edgeList = list(graph.edges())
        edgeColors = []
        edgeLabels = {}
        for u, v in edgeList:
            sign = str(graph[u][v].get("sign", "+")).strip()  # '+' or '-'
            if sign == "-":
                edgeColors.append("#b98980")
                edgeLabels[(u, v)] = "-"
            else:
                edgeColors.append("#8fa3a3")
                edgeLabels[(u, v)] = "+"
        # Draw edges first
        nx.draw_networkx_edges(
            graph, pos,
            edgelist=edgeList, edge_color=edgeColors,
            width=2.5, alpha=0.95,
            ax=ax
        )
        nx.draw_networkx_nodes(
            graph, pos,
            node_color=nodeColors, node_size=600,
            edgecolors="#4B2E2B",
            linewidths=1.5,
            ax=ax
        )
        nx.draw_networkx_edge_labels(
            graph, pos,
            edge_labels=edgeLabels,
            font_size=12,
            ax=ax
        )
        nx.draw_networkx_labels(graph, pos, ax=ax)
        
        pos_line = mlines.Line2D([], [], color="#8fa3a3", lw=2, label="Positive edge (+)")
        neg_line = mlines.Line2D([], [], color="#b98980", lw=2, label="Negative edge (-)")
        ax.legend(handles=[pos_line, neg_line])
        ax.set_title("Graph Attributes (Nodes colored by component)")
        ax.set_axis_off()
        plt.show()

#helper for calculating neighborhood overlap
def neighborhoodOverlap(G, u, v):
    Nu = set(G.neighbors(u))
    Nv = set(G.neighbors(v))
    union = Nu | Nv
    if len(union) == 0:
        return 0
    return len(Nu & Nv) / len(union)

#==============================================================================
# Verify Homophilly's: T test
#===============================================================================

#==============================================================================
# Verify Signed Balanced Graph
#===============================================================================

#==============================================================================
# Simulate Failures k : Verbose True: Executes for simulate command; false for robustness
#===============================================================================

#going with average path of graph or largest connected component
def avg_path(g):
    if g.number_of_nodes() <= 1:
        return 0.0, True
    if nx.is_connected(g):
        return nx.average_shortest_path_length(g), True
    largest = max(nx.connected_components(g), key=len)
    sub = g.subgraph(largest)
    if sub.number_of_nodes() <= 1:
        return 0.0, False
    return nx.average_shortest_path_length(sub), False

#helper for printing betweeness
def canon_edge(e):
    u, v = e
    return tuple(sorted((u, v)))

def simulate_failures(G, k, verbose=True):
    if verbose:
        print(f"\nSimulating Failures: Removing {k} Random Edge(s)")
        print("-" * 50)
    simulation = G.copy()
    # ----- Remove k random edges -----
    edges = list(simulation.edges())
    k = min(k, len(edges))
    removed_edges = []
    for i in range(k):
        idx = random.randrange(len(edges))
        u, v = edges.pop(idx)
        removed_edges.append((u, v))
        simulation.remove_edge(u, v)
        if verbose:
            print(f"  Removed Edge {i+1:>2}: ({u}, {v})")

    # ----- Connected components -----
    components = list(nx.connected_components(G))
    componentsNew = list(nx.connected_components(simulation))

    # ----- Average shortest path -----
    if verbose:
        print("\nAverage Shortest Path")
        print("-" * 50)
    avgOld, connectedOld = avg_path(G)
    avgNew, connectedNew = avg_path(simulation)

    if verbose:
        statusOld = "Connected" if connectedOld else "Disconnected (largest component)"
        statusNew = "Connected" if connectedNew else "Disconnected (largest component)"

        print(f"{'Graph':<12}{'Status':<35}{'Avg Path':>12}")
        print("-" * 65)
        print(f"{'Original':<12}{statusOld:<35}{avgOld:>12.4f}")
        print(f"{'Simulation':<12}{statusNew:<35}{avgNew:>12.4f}")

    # ----- Connected Components -----
    if verbose:
        print("\nConnected Components")
        print("-" * 50)

        print(f"{'Graph':<12}{'Total Components':>18}")
        print("-" * 30)
        print(f"{'Original':<12}{len(components):>18}")
        print(f"{'Simulation':<12}{len(componentsNew):>18}")
        print("\nOriginal Components")
        print("-" * 50)
        for i, comp in enumerate(components, start=1):
            print(f" Component {i:>2} | Size: {len(comp):>3} | Nodes: {sorted(comp)}")
        print("\nSimulation Components")
        print("-" * 50)
        for i, comp in enumerate(componentsNew, start=1):
            print(f" Component {i:>2} | Size: {len(comp):>3} | Nodes: {sorted(comp)}")
            
    # ----- Edge Betweenness -----
    betweenOld_raw = edgeBetweeness(G)
    betweenNew_raw = edgeBetweeness(simulation)
    betweenOld = {canon_edge(e): val for e, val in betweenOld_raw.items()}
    betweenNew = {canon_edge(e): val for e, val in betweenNew_raw.items()}
    if verbose:
        print("\nEdge Betweenness Centrality (Before vs After)")
        print("-" * 60)
        header = f"{'Edge':<18}{'Before':>10}{'After':>10}{'Change':>10}"
        print(header)
        print("-" * len(header))

        for edge in sorted(set(betweenOld) | set(betweenNew)):
            old_val = betweenOld.get(edge)
            new_val = betweenNew.get(edge)
            old_str = "N/A" if old_val is None else f"{old_val:.4f}"
            new_str = "N/A" if new_val is None else f"{new_val:.4f}"
            if old_val is None or new_val is None:
                delta_str = "N/A"
            else:
                delta_str = f"{(new_val - old_val):.4f}"
            print(f"{str(edge):<18}{old_str:>10}{new_str:>10}{delta_str:>10}")

    return {
        "simulation": simulation,
        "removed_edges": removed_edges,
        "avgOld": avgOld,
        "avgNew": avgNew,
        "num_components": len(componentsNew),
        "component_sizes": sorted(len(c) for c in componentsNew),
        "componentsNew": componentsNew
    }


#==============================================================================
# Robustness Check k - default 10 trials
#==============================================================================
def robustness_check(G, k, trials=10):
    random.seed(42)

    print(f"\nRobustness Check: {trials} Trial(s) of Removing {k} Random Edge(s)")
    print("-" * 140)
    # original clusters for persistence: using a threshold
    original_clusters = [set(c) for c in nx.connected_components(G)]
    persist_threshold = 0.90

    # one big table header (each trial is one row)
    header = (
        f"{'Trial':>5} | "
        f"{'Change in Avg Shortest Path':>28} | "
        f"{'Number of Connected Components':>30} | "
        f"{'Minimum Component Size':>22} | "
        f"{'Maximum Component Size':>22} | "
        f"{'Clusters Persist':>18}"
    )
    print(header)
    print("-" * len(header))

    comp_counts = []
    min_sizes = []
    max_sizes = []
    deltas = []
    persist_flags = []

    for t in range(1, trials + 1):
        result = simulate_failures(G, k, verbose=False)

        avgOld = result["avgOld"]
        avgNew = result["avgNew"]
        delta = (avgNew - avgOld) if (avgOld is not None and avgNew is not None) else None
        delta_str = "N/A" if delta is None else f"{delta:.4f}"

        sizes = result["component_sizes"]
        num_comp = result["num_components"]
        min_c = sizes[0] if sizes else 0
        max_c = sizes[-1] if sizes else 0

        # --- cluster persistence check ---
        new_clusters = [set(c) for c in result["componentsNew"]]

        persisted = 0
        for c_old in original_clusters:
            best_fraction = 0.0
            for c_new in new_clusters:
                fraction = len(c_old & c_new) / len(c_old)
                if fraction > best_fraction:
                    best_fraction = fraction
            if best_fraction >= persist_threshold:
                persisted += 1

        clusters_persist = "YES" if persisted == len(original_clusters) else "NO"
        persist_flags.append(persisted == len(original_clusters))

        # --- print one row ---
        print(
            f"{t:>5} | "
            f"{delta_str:>28} | "
            f"{num_comp:>30} | "
            f"{min_c:>22} | "
            f"{max_c:>22} | "
            f"{clusters_persist:>18}"
        )

        # --- collect for summary ---
        comp_counts.append(num_comp)
        min_sizes.append(min_c)
        max_sizes.append(max_c)
        if delta is not None:
            deltas.append(delta)

    avg_components = sum(comp_counts) / trials

    print("\nResults Summary Across All Trials")
    print("-" * 120)
    print(f"Average Number of Connected Components: {avg_components:.4f}")
    print(f"Max Components Observed: {max(comp_counts)}")
    print(f"Min Components Observed: {min(comp_counts)}")
    print(f"Smallest Component Size Observed: {min(min_sizes)}")
    print(f"Largest  Component Size Observed: {max(max_sizes)}")
    print(f"Clusters Persist in All Trials? {'YES' if all(persist_flags) else 'NO'}")

#==============================================================================
# Load a time series of edge changes in CSV format
#==============================================================================
def timeSeries(oldG, newG):
    pass
    

def main():
    args = parse_args()
    if args.input:
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
    if args.components:
        #optional robustness check
        if args.robustness_check:
            k = args.robustness_check
            robustness_check(G, k)
        G = partition(G, args.components)
        #output components in different files
        if args.split_output_dir:
            outputComponents(G)  
    if args.plot:
        print("About to plot:", G.number_of_nodes(), "nodes,", G.number_of_edges(), "edges")
        plot(G, args.plot)
    if args.verify_homophily:
        pass
    if args.output:
        outputFinal(G, args.output)
    
    if args.simulate_failures:
        k = args.simulate_failures
        simulate_failures(G, k)

    
    if args.temporal_simulation:
        pass
    
        
    

if __name__ == "__main__":
    main()
