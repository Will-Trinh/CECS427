import networkx as nx
import argparse
import matplotlib.pyplot as plt


# CECS 427: Assignment 3
# Oanh Tran 029661786
# William Trinh 030650397

# =============================================================================
# Argument Parsing
# =============================================================================
def parse_args():
    p = argparse.ArgumentParser(
        description="Read a directed graph from a .gml file and compute the Social Optimal and travel equilibrium."
    )
    p.add_argument("input", help="Input .gml graph file")
    p.add_argument("vehicles", type=int, help="Number of vehicles")
    p.add_argument("start", type=int, help="Start node")
    p.add_argument("end", type=int, help="Destination node")
    p.add_argument("--plot", action="store_true", help="Display the graph")
    return p.parse_args()


def read_graph_file(file):
    return nx.read_gml(file)

# =============================================================================
# helper: all the possible ways to distribute n vehicles across k paths
# =============================================================================
def splits(n, k):
    if k == 1:
        yield [n]
        return
    for i in range(n + 1):
        for r in splits(n - i, k - 1):
            yield [i] + r

# =============================================================================
# social optimum: calculate total travel costs of each different path splits and compare
# =============================================================================
def socialOptimum(G, n, start, end):
    paths = list(nx.all_simple_paths(G, start, end))
    bestCost = float("inf")
    bestFlow = None
    for split in splits(n, len(paths)):
        edgeFlow = {}
        # builds dictionary for number of vehicles on edge for current path
        for i, path in enumerate(paths):
            for u, v in zip(path[:-1], path[1:]):
                edgeFlow[(u, v)] = edgeFlow.get((u, v), 0) + split[i]
        # calculate cost function for edge to add to total social cost
        cost = 0
        for u, v in G.edges():
            x = edgeFlow.get((u, v), 0)
            a = float(G[u][v]["a"])
            b = float(G[u][v]["b"])
            cost += a * x * x + b * x
        #compare to best cost
        if cost < bestCost:
            bestCost = cost
            bestFlow = edgeFlow
            bestSplit = split
    return bestFlow, bestCost, paths, bestSplit

# =============================================================================
# Nash Equilibrium
# =============================================================================
def nashEq(G, n, start, end):
    paths = list(nx.all_simple_paths(G, start, end))
    bestPotential = float("inf")
    bestFlow = None
    bestSplit = None
    for split in splits(n, len(paths)):
        edgeFlow = {}
        for i, path in enumerate(paths):
            for u, v in zip(path[:-1], path[1:]):
                edgeFlow[(u, v)] = edgeFlow.get((u, v), 0) + split[i]
        # Rosenthal potential: sum over edges of sum_{k=1}^{x} (a*k + b)
        # = a * x*(x+1)/2 + b * x
        potential = 0
        for u, v in G.edges():
            x = edgeFlow.get((u, v), 0)
            a = float(G[u][v]["a"])
            b = float(G[u][v]["b"])
            potential += a * x * (x + 1) / 2 + b * x
        if potential < bestPotential:
            bestPotential = potential
            bestFlow = edgeFlow
            bestSplit = split
    # compute actual total travel cost at equilibrium
    totalCost = 0
    for u, v in G.edges():
        x = bestFlow.get((u, v), 0)
        a = float(G[u][v]["a"])
        b = float(G[u][v]["b"])
        totalCost += a * x * x + b * x
    return bestFlow, totalCost, paths, bestSplit

# =============================================================================
# plot
# =============================================================================
def plot(G, n):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize = (8, 6))
    nx.draw(G, pos, with_labels = True, node_color = "#C7CDBF", 
            node_size = 2000, arrows = True)
    labels = {}
    for u, v in G.edges():
        a = G[u][v]["a"]
        b = G[u][v]["b"]
        labels[(u, v)] = f"{a}x + {b}"
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Directed Graph")
    plt.show()
    plt.figure(figsize=(8, 6))
    xs = list(range(n + 1))
    for u, v in G.edges():
        a = float(G[u][v]["a"])
        b = float(G[u][v]["b"])
        ys = [a * x + b for x in xs]
        plt.plot(xs, ys, marker="o", label=f"{u}->{v}: {a}x + {b}")
    plt.xlabel("x (vehicles)")
    plt.ylabel("cost")
    plt.title("Edge Polynomials")
    plt.legend()
    plt.grid(True)
    plt.show()




def main():
    args = parse_args()
    try:
        G = read_graph_file(args.input)
    except Exception as e:
        print("Error reading file:", e)
        return
    start = str(args.start)
    end = str(args.end)
    numVehicles = args.vehicles
    if len(G.nodes()) == 0:
        print("Error: Graph is empty (no nodes).")
        return
    if start not in G:
        print(f"Error: Start node {start} not in graph.")
        return
    if end not in G:
        print(f"Error: End node {end} not in graph.")
        return
    if numVehicles < 0:
        print("Error: Number of vehicles must be nonnegative.")
        return
    if not nx.is_directed(G):
        print("Error: Graph must be directed.")
        return
    paths = list(nx.all_simple_paths(G, start, end))
    if len(paths) == 0:
        print(f"Error: No path exists from {start} to {end}.")
        return

    flow, cost, paths, split = socialOptimum(G, numVehicles, start, end)
    nFlow, nCost, nPaths, nSplit = nashEq(G, numVehicles, start, end)

    print("Paths:")
    for i, p in enumerate(paths):
        print(f"  P{i}: {' -> '.join(p)}")

    print("\n" + "="*50)
    print("Social Optimum")
    print("="*50)
    print("Edge Flows:")
    for u, v in G.edges():
        x = flow.get((u, v), 0)
        a = float(G[u][v]["a"])
        b = float(G[u][v]["b"])
        edgeCost = a * x * x + b * x
        print(f"  {u} -> {v}: {x} vehicles, cost = {edgeCost}")
    print("Path Flows:")
    for i, v in enumerate(split):
        print(f"  P{i}: {v} vehicles")
    print(f"Total Social Cost: {cost}")

    print("\n" + "="*50)
    print("Travel Equilibrium (Nash Equilibrium)")
    print("="*50)
    print("Edge Flows:")
    for u, v in G.edges():
        x = nFlow.get((u, v), 0)
        a = float(G[u][v]["a"])
        b = float(G[u][v]["b"])
        edgeCost = a * x * x + b * x
        print(f"  {u} -> {v}: {x} vehicles, cost = {edgeCost}")
    print("Path Flows:")
    for i, v in enumerate(nSplit):
        print(f"  P{i}: {v} vehicles")
    # show individual path costs at equilibrium
    print("Path Costs (per driver):")
    for i, p in enumerate(nPaths):
        pCost = sum(float(G[u][v]["a"]) * nFlow.get((u, v), 0) + float(G[u][v]["b"])
                    for u, v in zip(p[:-1], p[1:]))
        print(f"  P{i}: {pCost}")
    print(f"Total Travel Cost: {nCost}")


    if args.plot:
        plot(G, numVehicles)



if __name__ == "__main__":
    main()