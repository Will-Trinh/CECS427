import argparse
import networkx as nx
import os
import random
import matplotlib.pyplot as plt

# CECS 427: Assignment 6
# Oanh Tran 029661786
# William Trinh 030650397


# =============================================================================
# Argument Parsing
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Simulate spread across a network.")

    parser.add_argument("graph", help="Path to the GML graph file")
    parser.add_argument("--action", choices=["cascade", "covid"], required=True)
    parser.add_argument("--initiator", type=lambda s: [x.strip() for x in s.split(",")])
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--probability_of_infection", type=float)
    parser.add_argument("--probability_of_death", type=float, default=0.0)
    parser.add_argument("--lifespan", type=int, default=30, help="Simulates timestep of days")
    parser.add_argument("--shelter", type=float, default=0.0,
                        help="Proportion/rate (0-1) of nodes sheltered")
    parser.add_argument("--vaccination", type=float, default=0.0,
                        help="Proportion/rate of nodes vaccinated")
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--interactive", action="store_true")

    return parser.parse_args()


def loadGraph(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    try:
        graph = nx.read_gml(path)
    except Exception as e:
        raise ValueError(f"Error reading GML file: {e}")
    if len(graph.nodes()) == 0:
        raise ValueError("Graph loaded but contains no nodes")
    return graph


# =============================================================================
# Cascade — Linear Threshold Model
# =============================================================================

def _drawCascadeGraph(cascadeG, pos, title, save_path=None):
    """Draw cascade graph with active/inactive node coloring. Returns the figure."""
    node_colors = [
        "gold" if cascadeG.nodes[n]["state"] == "active" else "lightsteelblue"
        for n in cascadeG.nodes()
    ]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor("#f7f7f7")
    fig.patch.set_facecolor("#f7f7f7")
    nx.draw_networkx(
        cascadeG, pos, ax=ax,
        node_color=node_colors, node_size=400, font_size=8,
        edge_color="gray", alpha=0.9
    )
    ax.set_title(title, fontsize=12, fontweight="bold")
    handles = [
        plt.scatter([], [], s=80, color="gold",          edgecolors="black", linewidths=0.5, label="Active"),
        plt.scatter([], [], s=80, color="lightsteelblue", edgecolors="black", linewidths=0.5, label="Inactive"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    ax.axis("off")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120)
        print(f"  Plot saved to: {save_path}")
    return fig


def runCascade(graph, initiator, threshold, plot, interactive):
    """
    Linear Threshold cascade model.
    A node becomes active when >= threshold fraction of its neighbors are active.
    Updates are synchronous (snapshot-based) each round until no new activations occur.

    --interactive : display the graph state after every round
    --plot        : bar chart of new activations per round at the end
    """
    if not initiator:
        print("Error: No initiator nodes specified. Use --initiator to set starting nodes.")
        return

    if threshold is None:
        threshold = 0.5
        print(f"No --threshold specified, defaulting to {threshold}")

    nodes = set(graph.nodes())

    # Resolve initiator IDs. GML quoted labels are strings, so CLI strings match directly.
    resolved_initiators = []
    for raw in initiator:
        if raw in nodes:
            resolved_initiators.append(raw)
        else:
            print(f"Warning: Initiator node '{raw}' not found in graph, skipping.")

    if not resolved_initiators:
        print("Error: None of the specified initiator nodes were found in the graph.")
        print(f"  Available nodes: {sorted(nodes)}")
        return

    cascadeG = graph.copy()
    for node in cascadeG.nodes():
        cascadeG.nodes[node]["state"] = "inactive"
    for node in resolved_initiators:
        cascadeG.nodes[node]["state"] = "active"

    # activations_per_round[0] = count of initiator seeds (round 0)
    activations_per_round = [len(resolved_initiators)]

    print("=" * 40)
    print("CASCADE SIMULATION START")
    print("=" * 40)
    print(f"  Total nodes:  {len(cascadeG.nodes())}")
    print(f"  Threshold:    {threshold}")
    print(f"  Initiators:   {resolved_initiators}")
    print("=" * 40)

    pos = nx.spring_layout(cascadeG, seed=42)

    if interactive:
        plt.ion()
        active_count = len(resolved_initiators)
        fig = _drawCascadeGraph(
            cascadeG, pos,
            f"Cascade — Round 0 (Initiators) | Active: {active_count}/{len(cascadeG.nodes())}"
        )
        plt.pause(1.5)
        plt.close(fig)

    round_num = 0
    while True:
        round_num += 1
        new_active = []

        # Synchronous update: decisions based on start-of-round snapshot
        current_states = {n: cascadeG.nodes[n]["state"] for n in cascadeG.nodes()}

        for node in cascadeG.nodes():
            if current_states[node] == "active":
                continue
            neighbors = list(cascadeG.neighbors(node))
            if not neighbors:
                continue
            active_neighbors = sum(1 for nb in neighbors if current_states[nb] == "active")
            if active_neighbors / len(neighbors) >= threshold:
                new_active.append(node)

        if not new_active:
            print(f"Round {round_num}: No new activations — cascade has stabilized.")
            break

        for node in new_active:
            cascadeG.nodes[node]["state"] = "active"
            print(f"  Round {round_num}: Node {node} activated")

        activations_per_round.append(len(new_active))
        total_active = sum(1 for n in cascadeG.nodes() if cascadeG.nodes[n]["state"] == "active")
        print(f"Round {round_num}: {len(new_active)} new activations "
              f"(Total active: {total_active}/{len(cascadeG.nodes())})")
        print("-" * 40)

        if interactive:
            fig = _drawCascadeGraph(
                cascadeG, pos,
                f"Cascade — Round {round_num} | Active: {total_active}/{len(cascadeG.nodes())} "
                f"| New: {len(new_active)}"
            )
            plt.pause(1.5)
            plt.close(fig)

    if interactive:
        plt.ioff()

    total_active = sum(1 for n in cascadeG.nodes() if cascadeG.nodes[n]["state"] == "active")
    full_cascade = total_active == len(cascadeG.nodes())

    print("\n" + "=" * 40)
    print("CASCADE COMPLETE")
    print("=" * 40)
    print(f"  Nodes activated: {total_active} / {len(cascadeG.nodes())}")
    print(f"  Full cascade:    {'YES — all nodes reached' if full_cascade else 'NO — cascade stopped early'}")
    print("=" * 40)

    # Always output the final network graph
    fig = _drawCascadeGraph(
        cascadeG, pos,
        f"Cascade — Final State | Active: {total_active}/{len(cascadeG.nodes())} "
        f"| Full cascade: {'YES' if full_cascade else 'NO'}",
        save_path="cascade_final.png"
    )
    plt.show()
    plt.close(fig)

    # --plot: bar chart of new activations per round
    if plot:
        rounds = list(range(len(activations_per_round)))
        labels = ["Initiators"] + [f"Round {r}" for r in rounds[1:]]
        fig_plot, ax = plt.subplots(figsize=(10, 5))
        ax.bar(rounds, activations_per_round, color="steelblue", edgecolor="white")
        ax.set_xlabel("Round", fontsize=12)
        ax.set_ylabel("New Activations", fontsize=12)
        ax.set_title("Cascade — New Activations per Round", fontsize=14, fontweight="bold")
        ax.set_xticks(rounds)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("cascade_activations_per_round.png", dpi=150)
        print("Plot saved to: cascade_activations_per_round.png")
        plt.show()
        plt.close(fig_plot)


# =============================================================================
# COVID — SIRS model with modifications
# =============================================================================

"""
SIRS Modifications:
1. Vaccinated nodes: 0.25x infection probability (breakthrough infections still possible)
2. Immunity duration after recovery:
     - Unvaccinated recovered     → 90 days natural immunity
     - Vaccinated, never infected → 180 days vaccine immunity
     - Vaccinated and recovered   → 365 days hybrid immunity
3. Nodes can die (with given probability) after 10 days infected
4. Susceptible nodes with >50% infected neighbors may shelter-in-place for 14 days

Model Assumptions:
1. All vaccinated nodes are uninfected at the start (no hybrid immunity initially)
2. Recovered nodes cannot be reinfected until immunity wanes
3. Initial sheltered nodes began shelter at day 0
"""

# Node status → fill color. "V" (vaccinated, not yet infected) uses steelblue
# like Susceptible; a purple border distinguishes vaccinated nodes visually.
STATUS_COLOR = {
    "S":  "steelblue",
    "I":  "crimson",
    "R":  "seagreen",
    "D":  "dimgray",
    "SH": "goldenrod",
    "V":  "steelblue",
}


def initiateStatus(graph, initiators, vaccination, shelter):
    covidG = graph.copy()

    # Initialize all nodes as susceptible and reset tracking counters
    for node in covidG.nodes():
        covidG.nodes[node].update({
            "status": "S",
            "days_infected": 0,
            "days_sheltered": 0,
            "days_recovered": 0,
            "days_vaccinated": 0,
            "vaccinated": False
        })

    nodes = list(covidG.nodes())
    nonInitiators = [n for n in nodes if n not in initiators]

    # Vaccinate a random proportion of non-initiators
    if vaccination:
        vaccinated = random.sample(nonInitiators, int(vaccination * len(nonInitiators)))
        for node in vaccinated:
            covidG.nodes[node].update({
                "status": "V",
                "vaccinated": True,
                "days_vaccinated": 0
            })

    # Shelter a random proportion of remaining susceptible non-initiators
    if shelter:
        susceptible = [n for n in nonInitiators if covidG.nodes[n]["status"] == "S"]
        sheltered = random.sample(susceptible, int(shelter * len(susceptible)))
        for node in sheltered:
            covidG.nodes[node].update({
                "status": "SH",
                "days_sheltered": 0
            })

    # Initiators are set last so they always begin infected regardless of vaccination
    for node in initiators:
        if node in covidG.nodes():
            covidG.nodes[node].update({
                "status": "I",
                "days_infected": 0
            })

    return covidG


def plotCovidInteractive(covidG, pos, day):
    """Display the network state for one simulation day (interactive mode, non-blocking)."""
    node_colors     = [STATUS_COLOR[covidG.nodes[n]["status"]] for n in covidG.nodes()]
    node_edgecolors = [
        "mediumpurple" if covidG.nodes[n]["vaccinated"] else "white"
        for n in covidG.nodes()
    ]
    node_linewidths = [
        3.0 if covidG.nodes[n]["vaccinated"] else 0.5
        for n in covidG.nodes()
    ]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor("#f7f7f7")
    fig.patch.set_facecolor("#f7f7f7")

    totals = {
        s: sum(1 for n in covidG.nodes() if covidG.nodes[n]["status"] == s)
        for s in ["S", "I", "R", "D", "SH", "V"]
    }

    nx.draw_networkx_edges(covidG, pos, ax=ax, alpha=0.25, edge_color="gray", width=0.8)
    nx.draw_networkx_nodes(
        covidG, pos, ax=ax,
        node_color=node_colors,
        edgecolors=node_edgecolors,
        linewidths=node_linewidths,
        node_size=120,
    )

    label = "Initial State" if day == 0 else f"Day {day}"
    ax.set_title(
        f"COVID-19 Simulation — {label}  |  "
        f"S:{totals['S']}  I:{totals['I']}  R:{totals['R']}  "
        f"D:{totals['D']}  SH:{totals['SH']}  V:{totals['V']}",
        fontsize=11, fontweight="bold"
    )
    ax.axis("off")
    plt.tight_layout()
    plt.pause(1.0)
    plt.close(fig)


def plotCovidResults(covidG,
                     title="COVID-19 Network Simulation — Final Node Status",
                     save_path="covid_simulation_plot.png"):
    """
    Draws the final network graph with nodes colored by their status.
    Vaccinated nodes share the Susceptible fill color but have a purple border.
    """
    node_colors     = [STATUS_COLOR[covidG.nodes[n]["status"]] for n in covidG.nodes()]
    node_edgecolors = [
        "mediumpurple" if covidG.nodes[n]["vaccinated"] else "white"
        for n in covidG.nodes()
    ]
    node_linewidths = [
        3.0 if covidG.nodes[n]["vaccinated"] else 0.5
        for n in covidG.nodes()
    ]

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("#f7f7f7")
    fig.patch.set_facecolor("#f7f7f7")

    pos = nx.spring_layout(covidG, seed=42)

    nx.draw_networkx_edges(covidG, pos, ax=ax, alpha=0.25, edge_color="gray", width=0.8)
    nx.draw_networkx_nodes(
        covidG, pos, ax=ax,
        node_color=node_colors,
        edgecolors=node_edgecolors,
        linewidths=node_linewidths,
        node_size=120,
    )

    legend_entries = {
        "Susceptible (S)":            ("steelblue",  "white",        0.5),
        "Vaccinated (purple border)": ("steelblue",  "mediumpurple", 3.0),
        "Infected (I)":               ("crimson",    "white",        0.5),
        "Recovered (R)":              ("seagreen",   "white",        0.5),
        "Dead (D)":                   ("dimgray",    "white",        0.5),
        "Sheltered (SH)":             ("goldenrod",  "white",        0.5),
    }
    handles = [
        plt.scatter([], [], s=80, color=fc, edgecolors=ec, linewidths=lw, label=label)
        for label, (fc, ec, lw) in legend_entries.items()
    ]
    ax.legend(handles=handles, loc="upper left", framealpha=0.9, fontsize=9)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"\nPlot saved to: {save_path}")
    plt.show()


def runCovid(covidG, probability_of_infection, probability_of_death, lifespan,
             shelter, vaccination, plot=False, interactive=False):
    """
    SIRS simulation with shelter-in-place and vaccination modifiers.
    All state transitions use a start-of-day snapshot (synchronous update).

    --interactive : display the graph state after every day
    --plot        : bar chart of new infections per day at the end
    """
    probability_infection_V = probability_of_infection * 0.25

    total = {
        s: sum(1 for n in covidG.nodes() if covidG.nodes[n]["status"] == s)
        for s in ["S", "I", "R", "D", "SH", "V"]
    }

    print("=" * 40)
    print("COVID SIMULATION START")
    print("=" * 40)
    print(f"  Total nodes:                {len(covidG.nodes())}")
    print(f"  Probability of infection:   {probability_of_infection}")
    print(f"  Probability of death:       {probability_of_death}")
    print(f"  Shelter threshold:          {shelter}")
    print(f"  Vaccination rate:           {vaccination}")
    print(f"  Lifespan:                   {lifespan} days")
    print(f"  Initial S: {total['S']} | I: {total['I']} | V: {total['V']} | SH: {total['SH']}")
    print("=" * 40)

    totalInfected = total["I"]
    infections_per_day = []

    pos = nx.spring_layout(covidG, seed=42)
    if interactive:
        plt.ion()
        plotCovidInteractive(covidG, pos, 0)

    for i in range(lifespan):
        newInfections = 0
        newDeaths = 0
        newRecovered = 0
        # All transitions computed from start-of-day snapshot to prevent same-day chain effects
        current = {n: covidG.nodes[n].copy() for n in covidG.nodes()}
        updates = {}

        for node in covidG.nodes():
            status = current[node]["status"]
            if status == "D":
                continue
            # Skip nodes already scheduled for a status change this day
            if node in updates and "status" in updates[node]:
                continue

            if status == "I":
                new_days_infected = current[node]["days_infected"] + 1

                for neighbor in covidG.neighbors(node):
                    if neighbor in updates and "status" in updates[neighbor]:
                        continue
                    neighbor_status = current[neighbor]["status"]

                    if neighbor_status == "S":
                        if random.random() < probability_of_infection:
                            updates[neighbor] = {"status": "I", "days_infected": 0}
                            newInfections += 1
                            print(f"  Day {i+1}: Node {neighbor} infected by Node {node}")

                    elif neighbor_status == "V":
                        if random.random() < probability_infection_V:
                            # vaccinated flag stays True for hybrid immunity tracking
                            updates[neighbor] = {"status": "I", "days_infected": 0}
                            newInfections += 1
                            print(f"  Day {i+1}: Node {neighbor} breakthrough infection from Node {node}")

                # After 10 days infected: die or recover
                if new_days_infected >= 10:
                    if random.random() < probability_of_death:
                        updates[node] = {"status": "D", "days_infected": 0}
                        newDeaths += 1
                        print(f"  Day {i+1}: Node {node} has died")
                    else:
                        updates[node] = {"status": "R", "days_infected": 0, "days_recovered": 0}
                        newRecovered += 1
                        print(f"  Day {i+1}: Node {node} has recovered")
                else:
                    updates.setdefault(node, {})["days_infected"] = new_days_infected

            elif status == "SH":
                new_days_sheltered = current[node]["days_sheltered"] + 1
                if new_days_sheltered >= 14:
                    updates[node] = {"status": "S", "days_sheltered": 0}
                    print(f"  Day {i+1}: Node {node} left shelter")
                else:
                    updates.setdefault(node, {})["days_sheltered"] = new_days_sheltered

            elif status == "S":
                neighbors = list(covidG.neighbors(node))
                if neighbors and shelter:
                    infected_nb = sum(1 for nb in neighbors if current[nb]["status"] == "I")
                    if infected_nb / len(neighbors) > 0.5:
                        if random.random() < shelter:
                            updates[node] = {"status": "SH", "days_sheltered": 0}
                            print(f"  Day {i+1}: Node {node} entered shelter")

            elif status == "R":
                new_days_recovered = current[node]["days_recovered"] + 1
                immunityDays = 365 if current[node]["vaccinated"] else 90
                if new_days_recovered >= immunityDays:
                    updates[node] = {"status": "S", "days_recovered": 0}
                    print(f"  Day {i+1}: Node {node} immunity waned, returned to susceptible")
                else:
                    updates.setdefault(node, {})["days_recovered"] = new_days_recovered

            elif status == "V":
                new_days_vaccinated = current[node]["days_vaccinated"] + 1
                if new_days_vaccinated >= 180:
                    updates[node] = {"status": "S", "days_vaccinated": 0}
                    print(f"  Day {i+1}: Node {node} vaccine immunity waned, returned to susceptible")
                else:
                    updates.setdefault(node, {})["days_vaccinated"] = new_days_vaccinated

        # Apply all updates at end of day
        for node, attrs in updates.items():
            covidG.nodes[node].update(attrs)

        totalInfected += newInfections
        infections_per_day.append(newInfections)

        total = {
            s: sum(1 for n in covidG.nodes() if covidG.nodes[n]["status"] == s)
            for s in ["S", "I", "R", "D", "SH", "V"]
        }
        print(f"Day {i+1} | New infected: {newInfections} | "
              f"New recovered: {newRecovered} | New deaths: {newDeaths}")
        print(f"  Totals -> S: {total['S']} | I: {total['I']} | R: {total['R']} | "
              f"D: {total['D']} | SH: {total['SH']} | V: {total['V']}")
        print("-" * 40)

        if interactive:
            plotCovidInteractive(covidG, pos, i + 1)

    if interactive:
        plt.ioff()

    total = {
        s: sum(1 for n in covidG.nodes() if covidG.nodes[n]["status"] == s)
        for s in ["S", "I", "R", "D", "SH", "V"]
    }
    vaccinatedRecovered = sum(
        1 for n in covidG.nodes()
        if covidG.nodes[n]["vaccinated"] and covidG.nodes[n]["status"] == "R"
    )
    unvaccinatedRecovered = sum(
        1 for n in covidG.nodes()
        if not covidG.nodes[n]["vaccinated"] and covidG.nodes[n]["status"] == "R"
    )

    print("\n" + "=" * 40)
    print("SIMULATION COMPLETE")
    print("=" * 40)
    print(f"  Total nodes:                          {sum(total.values())}")
    print(f"  Total infected (cumulative):          {totalInfected}")
    print()
    print("  CURRENT STATUS:")
    print(f"  Susceptible:                                   {total['S']}")
    print(f"  Infected:                                      {total['I']}")
    print(f"  Total Recovered (Including Vaccinated):        {total['R']}")
    print(f"  Dead:                                          {total['D']}")
    print(f"  Sheltered:                                     {total['SH']}")
    print()
    print("  IMMUNITY STATUS:")
    print(f"  Vaccinated (never infected):    {total['V']}  -> immunity wanes at 180 days")
    print(f"  Recovered (unvaccinated):       {unvaccinatedRecovered}  -> natural immunity wanes at 90 days")
    print(f"  Recovered (vaccinated):         {vaccinatedRecovered}  -> hybrid immunity wanes at 365 days")
    assert vaccinatedRecovered + unvaccinatedRecovered == total['R'], "Recovered count mismatch!"
    print("=" * 40)

    # Always output the final network graph
    plotCovidResults(covidG)

    # --plot: bar chart of new infections per day
    if plot:
        days = list(range(1, lifespan + 1))
        fig_plot, ax = plt.subplots(figsize=(12, 5))
        ax.bar(days, infections_per_day, color="crimson", edgecolor="white", alpha=0.85)
        ax.set_xlabel("Day", fontsize=12)
        ax.set_ylabel("New Infections", fontsize=12)
        ax.set_title("COVID-19 Simulation — New Infections per Day",
                     fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig("covid_infections_per_day.png", dpi=150)
        print("Plot saved to: covid_infections_per_day.png")
        plt.show()
        plt.close(fig_plot)


# =============================================================================
# Main
# =============================================================================

def main():
    args = parse_args()

    try:
        graph = loadGraph(args.graph)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return

    if args.action == "cascade":
        if args.initiator is None:
            print("Error: --initiator is required for the cascade action.")
            return
        runCascade(graph, args.initiator, args.threshold, args.plot, args.interactive)

    elif args.action == "covid":
        if args.initiator is None:
            print("Error: --initiator is required for the covid action.")
            return
        if args.probability_of_infection is None:
            print("Error: --probability_of_infection is required for the covid action.")
            return
        covidG = initiateStatus(graph, args.initiator, args.vaccination, args.shelter)
        runCovid(
            covidG,
            args.probability_of_infection,
            args.probability_of_death,
            args.lifespan,
            args.shelter,
            args.vaccination,
            plot=args.plot,
            interactive=args.interactive,
        )


if __name__ == "__main__":
    main()
