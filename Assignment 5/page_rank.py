import networkx as nx
import argparse
from fractions import Fraction
from spider import runSpider
# CECS 427: Assignment 4
# Oanh Tran 029661786
# William Trinh 030650397

#Check - if crawler returns non star graphs and pageRank executes without error 
# i have not checked/added some edge cases - invalid crawler file format, empty graph file/missing file


# =============================================================================
# Argument Parsing
# =============================================================================
def parse_args():
    p = argparse.ArgumentParser(
        description="Web crawler that uses the PageRank algorithm to determine the importance of web pages based on their links."
    )
    p.add_argument("--crawler", type=str, default=None, help="Input crawler file (e.g., crawler.txt)")
    p.add_argument("--input", type=str, default=None, help="Input .gml graph file (e.g., graph.gml)")
    p.add_argument("--loglogplot", action="store_true", help="Display log-log plot of PageRank distribution")
    p.add_argument("--crawler_graph", type=str, default=None, help="Output .gml graph file from crawler (e.g., out_graph.gml)")
    p.add_argument("--pagerank_values", type=str, default=None, help="Output file for PageRank values (e.g., node_rank.txt)")
    return p.parse_args()


# =============================================================================
# Helpers
# =============================================================================
def readGraph(file):
    try:
        return nx.read_gml(file)
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except Exception as e:
        print("Error reading graph file:", e)
        raise

def readTextFile(file):
    try:
        with open(file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except Exception as e:
        print("Error reading text file:", e)
        raise
    

#maybe error handling for invalid crawler file format 


# =============================================================================
# Loglog plot: Generates a log-log plot of the degree distribution of the graph
# =============================================================================
# Todo -



# =============================================================================
# pageRank: Implements the PageRank algorithm to compute the importance of each node in the graph
# =============================================================================
#k is the limit number of iterations to run the PageRank algorithm.
#define stopping point to be when values change by less than 1e-6 or after k iterations, whichever comes first.

def pageRank(graph, k=100, tol=1e-6, outputFile="node_rank.txt"):
    n = graph.number_of_nodes()
    pageRankValues = {node: 1 / n for node in graph.nodes()}
    nodes = list(graph.nodes())
    print("Running PageRank algorithm for up to", k, "iterations...")

    print(f"Initial PageRank values:")
    for node in nodes:
        print(f"Node: {node}, PageRank: {Fraction(pageRankValues[node]).limit_denominator(1000)}")

    for i in range(k):
        newPageRankValues = {}
        for node in nodes:
            shares = 0
            for predecessor in graph.predecessors(node):
                if graph.out_degree(predecessor) > 0:
                    shares += pageRankValues[predecessor] / graph.out_degree(predecessor)
            # If node has no outgoing links, it keeps its own rank
            if graph.out_degree(node) == 0:
                shares += pageRankValues[node]
            newPageRankValues[node] = shares

        diff = sum(abs(newPageRankValues[node] - pageRankValues[node]) for node in nodes)
        pageRankValues = newPageRankValues

        if diff < tol:
            print(f"Converged after {i + 1} iterations.")
            break

    print(f"Final PageRank values after {i + 1} iterations:")
    for node in nodes:
        print(f"Node: {node}, PageRank: {Fraction(pageRankValues[node]).limit_denominator(1000)}")

    print(f"Writing PageRank values to file '{outputFile}'...")
    with open(outputFile, "w") as f:
        for node in nodes:
            label = graph.nodes[node].get('label', node)
            f.write(f"Node: {label}, PageRank: {Fraction(pageRankValues[node]).limit_denominator(1000)}\n")
    return pageRankValues

def main():
    args = parse_args()
    graph = None

    if args.crawler:
        outputFile = args.crawler_graph if args.crawler_graph else "out_graph.gml"
        runSpider(args.crawler, outputFile)
        graph = readGraph(outputFile)
        
    elif args.input:
        graph = readGraph(args.input)
        if graph:
            print(f"Loaded graph from '{args.input}' with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")

    if graph and args.pagerank_values:
        pageRank(graph, k=100, outputFile=args.pagerank_values)
        print(f"PageRank values written to '{args.pagerank_values}'.")
        
    elif graph:
        pageRank(graph, k=100, outputFile="node_rank.txt")

    if args.loglogplot and graph:
        # TODO: display log-log plot
        pass


if __name__ == "__main__":
    main()