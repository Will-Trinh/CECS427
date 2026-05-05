import argparse
import networkx as nx
import os
import random

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
    parser.add_argument("--probability_of_death", type=float)
    parser.add_argument("--lifespan", type=int, help = "Simulates timestep of days")
    parser.add_argument("--shelter", type=float, help ="Proportion/rate (0-1) of nodes sheltered")
    parser.add_argument("--vaccination", type=float, help = "Proportion/rate of nodes vaccinated")
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

#Either simulates a cascading effect through the network (e.g., information spread) or 
# simulates the spread of a pandemic like COVID-19 across the network.

def runCascade(graph, initiator, threshold, plot, interactive):
    pass



#Plot the graph and the state of the nodes for every round
""" S - blue, I - red, R - green, D - black, SH - yellow, V - purple """


# =============================================================================
# Covid - SIRS model with modifications
# =============================================================================
def initiateStatus(graph, initiators, vaccination, shelter):
    covidG = graph.copy()

    # Initialize all nodes as susceptible by default and set tracking fields
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
    # Vaccinated nodes start in status V and have reduced infection probability
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

    # Initiators are set last so they always begin infected
    for node in initiators:
        if node in covidG.nodes():
            covidG.nodes[node].update({
                "status": "I",
                "days_infected": 0
            })

    return covidG


"""
SIRS Modifications Start
1. At start: vaccinated nodes still have a probability of infection; but at a much lower rate: 0.25 * probability of infection param. (true/false for vaccinated field)
2. Infected nodes that recover: nodes not vaccinated have immunity - 90 days, vaccinated nodes uninfected - 180 days,  vaccinated nodes infected have immunity - 365 days; which is tracked through the simulation. 
3. when immunity wanes off, node re-enters susceptible. 
4. Nodes can die determined by probability after 10 days
5. If a node has majority of neighbors infected, generate random number with threshold of (shelter prob) to determine the node will take shelter, shelter length is determined by 14 days 

Model Assumptions
1. All vaccinated nodes have not been infected previously - assume no hybrid immunity, and still "susceptible" but with lower rate of infection
2. Assume recovered nodes can not be reinfected or enter susceptibility until immunity wanes off
3. Initial nodes in shelter started shelter at day 0
4. 

"""

def runCovid(covidG, probability_of_infection, probability_of_death, lifespan, shelter, vaccination):
    # Vaccinated nodes have lower infection probability than unvaccinated nodes
    probability_infected = probability_of_infection
    probability_infection_V = probability_infected * 0.25

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

    for i in range(lifespan):
        newInfections = 0
        newDeaths = 0
        newRecovered = 0
        # Synchronous update model: all transitions are computed from the start-of-day snapshot and applied at the end of the day to prevent same-day chain effects
        current = {n: covidG.nodes[n].copy() for n in covidG.nodes()}
        updates = {}

        for node in covidG.nodes():
            status = current[node]["status"]
            # Dead nodes do not change state
            if status == "D":
                continue
            # If a node already has a state change scheduled for today,
            # do not process it again in the same timestep
            if node in updates and "status" in updates[node]:
                continue
            # Infected node logic: attempt to infect neighbors, then possibly recover or die
            if status == "I":
                new_days_infected = current[node]["days_infected"] + 1
                # Infection attempts are based only on the start-of-day state
                for neighbor in covidG.neighbors(node):
                    # If neighbor already has a state transition scheduled today, skip it
                    if neighbor in updates and "status" in updates[neighbor]:
                        continue
                    neighbor_status = current[neighbor]["status"]

                    if neighbor_status == "S":
                        if random.random() < probability_infected:
                            updates[neighbor] = {
                                "status": "I",
                                "days_infected": 0
                            }
                            newInfections += 1
                            print(f"  Day {i+1}: Node {neighbor} infected by Node {node}")

                    elif neighbor_status == "V":
                        if random.random() < probability_infection_V:
                            # Breakthrough infection - when vaccinated node gets infected
                            # vaccinated flag stays True for later hybrid immunity tracking
                            updates[neighbor] = {
                                "status": "I",
                                "days_infected": 0
                            }
                            newInfections += 1
                            print(f"  Day {i+1}: Node {neighbor} breakthrough infection from Node {node}")

                # After 10 days infected, node either dies or recovers
                if new_days_infected >= 10:
                    if random.random() < probability_of_death:
                        updates[node] = {
                            "status": "D",
                            "days_infected": 0
                        }
                        newDeaths += 1
                        print(f"  Day {i+1}: Node {node} has died")
                    else:
                        updates[node] = {
                            "status": "R",
                            "days_infected": 0,
                            "days_recovered": 0
                        }
                        newRecovered += 1
                        print(f"  Day {i+1}: Node {node} has recovered")
                else:
                    if node not in updates:
                        updates[node] = {}
                    updates[node]["days_infected"] = new_days_infected

            # Sheltered nodes are temporarily removed from transmission
            elif status == "SH":
                new_days_sheltered = current[node]["days_sheltered"] + 1

                if new_days_sheltered >= 14:
                    updates[node] = {
                        "status": "S",
                        "days_sheltered": 0
                    }
                    print(f"  Day {i+1}: Node {node} left shelter")
                else:
                    if node not in updates:
                        updates[node] = {}
                    updates[node]["days_sheltered"] = new_days_sheltered

            # Susceptible nodes may enter shelter if the majority of neighbors are infected
            elif status == "S":
                infectedNeighbors = sum(
                    1 for n in covidG.neighbors(node)
                    if current[n]["status"] == "I"
                )
                totalNeighbors = len(list(covidG.neighbors(node)))

                if totalNeighbors > 0 and infectedNeighbors / totalNeighbors > 0.5:
                    if random.random() < shelter:
                        updates[node] = {
                            "status": "SH",
                            "days_sheltered": 0
                        }
                        print(f"  Day {i+1}: Node {node} entered shelter")

            # SIRS logic: recovered nodes eventually become susceptible again
            elif status == "R":
                new_days_recovered = current[node]["days_recovered"] + 1

                # Hybrid immunity lasts longer than natural immunity
                immunityDays = 365 if current[node]["vaccinated"] else 90

                if new_days_recovered >= immunityDays:
                    updates[node] = {
                        "status": "S",
                        "days_recovered": 0
                    }
                    print(f"  Day {i+1}: Node {node} immunity waned, returned to susceptible")
                else:
                    if node not in updates:
                        updates[node] = {}
                    updates[node]["days_recovered"] = new_days_recovered

            # Vaccinated nodes can lose vaccine protection over time if never infected
            elif status == "V":
                new_days_vaccinated = current[node]["days_vaccinated"] + 1

                if new_days_vaccinated >= 180:
                    updates[node] = {
                        "status": "S",
                        "days_vaccinated": 0
                    }
                    print(f"  Day {i+1}: Node {node} vaccine immunity waned, returned to susceptible")
                else:
                    if node not in updates:
                        updates[node] = {}
                    updates[node]["days_vaccinated"] = new_days_vaccinated

        # Apply all updates once at the end of the day
        for node, attrs in updates.items():
            covidG.nodes[node].update(attrs)
        totalInfected += newInfections
        total = {
            s: sum(1 for n in covidG.nodes() if covidG.nodes[n]["status"] == s)
            for s in ["S", "I", "R", "D", "SH", "V"]
        }
        print(f"Day {i+1} | New infected: {newInfections} | New recovered: {newRecovered} | New deaths: {newDeaths}")
        print(f"  Totals -> S: {total['S']} | I: {total['I']} | R: {total['R']} | D: {total['D']} | SH: {total['SH']} | V: {total['V']}")
        print("-" * 40)
    total = {
        s: sum(1 for n in covidG.nodes() if covidG.nodes[n]["status"] == s)
        for s in ["S", "I", "R", "D", "SH", "V"]
    }
    # These counts are current end-of-simulation recovered nodes, not cumulative recoveries
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
    print(f"  Total infected:                       {totalInfected}")
    print()
    print("  CURRENT STATUS:")
    print(f"  Susceptible:                                   {total['S']}")
    print(f"  Infected:                                      {total['I']}")
    print(f"  Total Recovered (Including Vaccinated):        {total['R']}")
    print(f"  Dead:                                          {total['D']}")
    print(f"  Sheltered:                                     {total['SH']}")
    print()
    print("  IMMUNITY STATUS:")
    print(f"  Vaccinated (never infected):    {total['V']}  → immunity wanes at 180 days")
    print(f"  Recovered (unvaccinated):       {unvaccinatedRecovered}  → natural immunity wanes at 90 days")
    print(f"  Recovered (vaccinated):         {vaccinatedRecovered}  → hybrid immunity wanes at 365 days")
    assert vaccinatedRecovered + unvaccinatedRecovered == total['R'], "Recovered count mismatch!"
    print("=" * 40)
    
def main():
    args = parse_args()

    try:
        open(args.graph)
    except FileNotFoundError:
        print(f"Error: File '{args.graph}' not found.")
        return

    graph = loadGraph(args.graph)

    if args.action == "cascade":
        runCascade(graph, args.initiator, args.threshold, args.plot, args.interactive)

    elif args.action == "covid":
        covidG = initiateStatus(graph, args.initiator, args.vaccination, args.shelter)
        runCovid(covidG, args.probability_of_infection, args.probability_of_death,
                args.lifespan, args.shelter, args.vaccination)


if __name__ == "__main__":
    main()