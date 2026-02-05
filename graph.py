import networkx as nx
from matplotlib.lines import Line2D

import math
import random
import argparse
from collections import deque
from matplotlib import pyplot as plt
#CECS 427: Assignment 1
#Oanh Tran 029661786
#

"""
Argument Parsing: 
"""
def parse_args(argv=None):
    p = argparse.ArgumentParser()
    #arg input graph file overided
    p.add_argument("--input", type=str)
    #args create random graph n, c -> datatypes converted/checked later
    p.add_argument("--create_random_graph", nargs=2, type=float, metavar=("n", "c"))
    #args a1, a2, a3 etc for multi bfs
    p.add_argument("--multi_BFS", nargs="+", type=str)
    p.add_argument("--analyze", action="store_true")
    p.add_argument("--plot", action="store_true")
    #args output graph gml file
    p.add_argument("--output", type=str)
    return p

#read file
def graph_file(file: str):
    return nx.read_gml(file)

#---------------------------------------------------------------------------#
"""Generate Random Graph -> Erdős–Rényi model"""
def generate_graph(n: int, c: float):
    G = nx.Graph()
    G.add_nodes_from([str(i) for i in range(n)]) 
    #probability of edge
    p = ((c*math.log(n))/n)
    #add nodes with labels "0" to "n-1"
    for i in range(n): #for each node pair, generate a random number and if it is less than the probability p, add edge
        label = str(i)
        G.add_node(label)
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                G.add_edge(str(i), str(j))
            else:
                continue
    return G


#--------------------------------------------------------------------------------#
"""Breadth First Search"""
# bfs function for one start node
def bfs(graph, start):
    visited = []
    parent = {}         
    queue = deque([start])
    visited = {start}
    parent[start] = None 
    print("Visited: ",end=" ")
    while queue:
        node = queue.popleft()
        print(node, end =", ")
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node 
                queue.append(neighbor)
                
    print("\n")

    return parent

#to see the bfs tree 
def printBFS(parent, start):
    children = {}
    for node, par in parent.items():
        children.setdefault(node, [])
        if par is not None:
            children.setdefault(par, []).append(node)
    for k in children:
        children[k].sort()
    def dfs(node, prefix="", is_last=True):
        if prefix == "":
            print("   " + node)
        else:
            print(prefix + ("└─ " if is_last else "├─ ") + node)
        kids = children.get(node, [])
        new_prefix = prefix + ("   " if is_last else "│  ")
        for i, child in enumerate(kids):
            dfs(child, new_prefix, i == len(kids) - 1)
    dfs(start)

#perform BF on many nodes using BFs and print trees for each
def multiBFS(G, *start_nodes):
    for node in start_nodes: 
        if node not in G.nodes:
            raise ValueError(f"Node {node} does not exist in the graph")
        print(f"\nRunning BFS from {node}")
        nodeBFS = bfs(G, node) 
        printBFS(nodeBFS, node)
        #maybe return node and their edges to use for plot function idk wht
    
#------------------------------------------------------------------------------#
def analysis(G):
    edges = G.number_of_edges()
    nodes = G.number_of_nodes()
    maxPossibleEdges = nodes * (nodes - 1)//2
    components = list(nx.connected_components(G))
    print("\n----------------Analysis----------------")
    num = 0
    for i, comp in enumerate(components):
        if len(comp) > 1:
            print(f"Connected Component {i+1}:", comp)
            num+=1
    print(f"\nTotal Connected Components: {num}")
            
    cycles = nx.cycle_basis(G)
    
    if cycles:
        print("\nCycles found:")
        for i, cycle in enumerate(cycles, 1):
            print(f"Cycle {i}: {' -> '.join(cycle)} -> {cycle[0]}")
    else:
        print("\nNo cycles found!")
        
    isolated = list(nx.isolates(G))
    if isolated:
        print("\nIsolated nodes:", isolated)
    else:
        print("\nNo isolated nodes")   
        
    graphDensity = edges/maxPossibleEdges
    print(f"\nGraph Density: {graphDensity}")
    
    if nx.is_connected(G):
        avg_len = nx.average_shortest_path_length(G)
        print("\nAverage shortest path length:", avg_len)
    else:
        print("\nGraph is not connected; average shortest path length is undefined")
    print("-------------------End-------------------")


#-------------------------------------------------------------------------------
#make edge color different for BFS paths 
#make isolated nodes different color
#change color for isolated nodes

#so far this is just the graph without diff colors or highlighted bfs paths 
def plot(G):
    isolatedNodes = list(nx.isolates(G))
    normalNodes = [node for node in G.nodes() if node not in isolatedNodes]
    
    #legends for color meanings
    legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Normal Node',
            markerfacecolor="#95B18E", markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Isolated Node',
            markerfacecolor="#9D5B5B", markersize=10)]

    plt.legend(handles=legend_elements)
    
    pos = nx.spring_layout(G, k=1.2, iterations=50, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="#9FB699", edge_color="#8E7863", width = 2, font_size=10, font_weight='bold', node_size=500)
    plt.title("Generated Erdős–Rényi Random Graph", fontsize=14)
    plt.show()
    plt.savefig("network_plot.png", format="PNG", dpi=300)

    

#put graph to gml file
def output_graph(G, file: str):
    pass



def main():
    parser = parse_args()         
    args = parser.parse_args()    
    
    if args.create_random_graph:
        n, c = args.create_random_graph
        try:
            #converting to proper data types
            n = int(args.create_random_graph[0])
            c = float(args.create_random_graph[1])
        except ValueError:
            parser.error(f"--create_random_graph n must be an integer, and c must be a valid number")
        if n <= 0 or c<=0:
            parser.error("--create_random_graph n and c must be > 0")
        #generate graph
        G = generate_graph(int(n), float(c))
        print("Nodes:", G.nodes())
        print("Number of nodes:", G.number_of_nodes())
        print("Number of edges:", G.number_of_edges())
        print("Edges:", list(G.edges()))
        
    #multi BFS
    if args.multi_BFS:
        try:
            edges=multiBFS(G, *args.multi_BFS)
        except ValueError as e:
            print(e)
    
    if args.analyze:
        analysis(G)
    
    if args.plot:
        plot(G)
    
    #if args.output:
        pass

    

if __name__ == "__main__":
    main()