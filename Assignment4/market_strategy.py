import networkx as nx
import argparse
import matplotlib.pyplot as plt


# CECS 427: Assignment 4
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
    p.add_argument("--plot", action="store_true", help="Display the graph")
    p.add_argument("--interactive", action="store_true", help="Shows output of every round graph")

    return p.parse_args()


def read_graph_file(file):
    return nx.read_gml(file)

#================================================================================
#plot
#================================================================================
def plot(G, title="Graph"):
    import matplotlib.pyplot as plt

    sellers = [n for n, d in G.nodes(data=True) if d.get("bipartite") == 0]
    buyers = [n for n, d in G.nodes(data=True) if d.get("bipartite") == 1]

    sellers = list(sellers)
    buyers = list(buyers)

    pos = {}

# The code snippet you provided is setting the positions of the nodes in the graph visualization.
    for i, s in enumerate(sellers):
        pos[s] = (0, -i)

    for i, b in enumerate(buyers):
        pos[b] = (3, -i)
        
    plt.text(0, 0.2, "Sellers", fontsize=10, ha='center', fontweight='bold')
    plt.text(3, 0.2, "Buyers", fontsize=10, ha='center', fontweight='bold')

    nx.draw_networkx_nodes(G, pos, nodelist=sellers, node_color= "lightblue", node_shape='o', node_size=800)
    nx.draw_networkx_nodes(G, pos, nodelist=buyers, node_color = "lightgray", node_shape='o', node_size=800)
    nx.draw_networkx_edges(G, pos)

    labels = {}
    for s in sellers:
        labels[s] = f"{s}\np={G.nodes[s].get('price', 0)}"
    for b in buyers:
        labels[b] = str(b)

    nx.draw_networkx_labels(G, pos, labels)

    #  edge labels 
    for (u, v, data) in G.edges(data=True):
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        x = x1 + 0.75 * (x2 - x1)
        y = y1 + 0.75 * (y2 - y1)
        plt.text(
            x, y,
            str(data.get("valuation", "")),
            fontsize=10,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.2)
        )
    plt.title(title)
    plt.axis("off")
    plt.show()

#==================================================================================
#interactive - seller preference 
#==================================================================================


def sellerPreference(G):
    sellerP = nx.Graph()
    sellers = []
    buyers = []

    for node, data in G.nodes(data=True):
        sellerP.add_node(node, **data)
        if data.get("bipartite") == 0:
            sellers.append(node)
        elif data.get("bipartite") == 1:
            buyers.append(node)

    for buyer in buyers:
        bestValuation = None
        preference = []

        for seller in sellers:
            if G.has_edge(seller, buyer):
                valuation = G[seller][buyer].get("valuation", 0)
                price = G.nodes[seller].get("price", 0)
                newValue = valuation - price

                if bestValuation is None or newValue > bestValuation:
                    bestValuation = newValue
                    preference = [seller]
                elif newValue == bestValuation:
                    preference.append(seller)

        for seller in preference:
            sellerP.add_edge(seller, buyer)

    return sellerP


def marketClearing(G, interactive=False):
    sellers = [n for n, d in G.nodes(data=True) if d.get("bipartite") == 0]
    buyers = [n for n, d in G.nodes(data=True) if d.get("bipartite") == 1]
    for s in sellers:
        if "price" not in G.nodes[s]:
            G.nodes[s]["price"] = 0
    round_num = 0
    while True:
        P = sellerPreference(G)
        matching = nx.algorithms.bipartite.maximum_matching(P, top_nodes=set(buyers))
        matched_buyers = {b: matching[b] for b in buyers if b in matching}
        if interactive:
            print("\n" + "="*40)
            print(f"ROUND {round_num}")
            print("="*40)

            # Prices
            print("Prices:")
            for s in sellers:
                print(f"  s{s}: {G.nodes[s]['price']}")

            # Updated valuations (v - price)
            print("\nUpdated Valuations (v - price):")
            for b in buyers:
                print(f"  Buyer {b}:", end=" ")
                vals = []
                for s in sellers:
                    if G.has_edge(s, b):
                        v = G[s][b]["valuation"]
                        p = G.nodes[s]["price"]
                        vals.append(f"s{s}:{v - p}")
                print(", ".join(vals))
            # Preference edges
            print("\nPreferences:")
            for s, b in P.edges():
                print(f"  {b} -> {s}")
            # Matching
            print("\nMatching:")
            if matched_buyers:
                for b, s in matched_buyers.items():
                    print(f"  {b} -> {s}")
            else:
                print("  None")

            # Unmatched
            unmatched = [b for b in buyers if b not in matched_buyers]
            print("\nUnmatched:", unmatched)
            # Overdemanded sellers
            overdemanded = set()
            for b in unmatched:
                for s in P.neighbors(b):
                    overdemanded.add(s)
            print("Raise prices of:", list(overdemanded))
        # Unmatched buyers
        unmatched_buyers = [b for b in buyers if b not in matched_buyers]
        print("\nUnmatched Buyers:", unmatched_buyers)
        # Over demanded sellers
        overdemanded_sellers = set()
        for b in unmatched_buyers:
            for s in P.neighbors(b):
                overdemanded_sellers.add(s)
        print("Overdemanded Sellers:", list(overdemanded_sellers))
        if len(matched_buyers) == len(buyers):
            return matched_buyers
        unmatched_buyers = [b for b in buyers if b not in matched_buyers]
        overdemandSellers = set()
        for b in unmatched_buyers:
            for s in P.neighbors(b):
                overdemandSellers.add(s)
        for s in overdemandSellers:
            G.nodes[s]["price"] += 1
        round_num += 1
        
        
def main():
    args = parse_args()

    try:
        G = read_graph_file(args.input)
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print("Error:", e)
    
    if args.plot:
        plot(G)
    if args.interactive:
        # run market clearing
        matching = marketClearing(G, interactive=args.interactive)
        # final output
        print("\n=== Final Result ===")
        print("Matching:", matching)
        print("Final Prices:")
        for node, data in G.nodes(data=True):
            if data.get("bipartite") == 0:
                print(f"Seller {node}: {G.nodes[node]['price']}")


if __name__ == "__main__":
    main()
