# Assignment 6 — Dynamic Population Simulation

**CECS 427**  
Oanh Tran (029661786) · William Trinh (030650397)

---

## Overview

`dynamic_population.py` simulates the spread of a phenomenon across a network loaded from a GML file. Two modes are supported:

- **cascade** — Linear Threshold Model: information/behavior spreads when enough neighbors adopt it.
- **covid** — SIRS Model with vaccination and shelter-in-place extensions.

---

## Requirements

```
pip install networkx matplotlib
```

Python 3.8 or later.

---

## Usage

```
python ./dynamic_population.py <graph.gml> --action [cascade|covid] [options]
```

### Parameters

| Parameter | Description |
|---|---|
| `graph.gml` | Path to the GML graph file (required) |
| `--action` | `cascade` or `covid` (required) |
| `--initiator m` | Comma-separated starting node IDs, e.g. `1,2,5` (required) |
| `--threshold q` | Cascade threshold (0–1); fraction of active neighbors required to activate a node. Defaults to `0.5` if omitted. |
| `--probability_of_infection p` | Per-contact probability of infection (required for covid) |
| `--probability_of_death q` | Probability of death after 10 days infected. Default: `0.0` |
| `--lifespan l` | Number of simulation days/rounds. Default: `30` |
| `--shelter s` | Proportion (0–1) of susceptible nodes that shelter-in-place when >50% of their neighbors are infected. Default: `0.0` |
| `--vaccination r` | Proportion (0–1) of non-initiator nodes that are vaccinated at the start. Default: `0.0` |
| `--plot` | Show a bar chart of new activations/infections per round/day after the simulation |
| `--interactive` | Display the graph state after every round/day (1-second pause per frame) |

---

## Examples

### Cascade

```bash
python ./dynamic_population.py cascadebehaviour.gml --action cascade --initiator 1,2,5 --threshold 0.33 --plot
```

Runs the cascade starting from nodes 1, 2, and 5 with a threshold of 0.33. Outputs `cascade_final.png` (always) and `cascade_activations_per_round.png` (with `--plot`).

```bash
python ./dynamic_population.py cascadebehaviour.gml --action cascade --initiator 1 --threshold 0.5 --interactive
```

Shows the graph state after every round as the cascade propagates.

### COVID

```bash
python ./dynamic_population.py cascadebehaviour.gml --action covid --initiator 3,4 --probability_of_infection 0.02 --lifespan 100 --shelter 0.3 --vaccination 0.24
```

Runs the SIRS simulation for 100 days starting from nodes 3 and 4. Outputs `covid_simulation_plot.png`.

```bash
python ./dynamic_population.py cascadebehaviour.gml --action covid --initiator 1 --probability_of_infection 0.05 --probability_of_death 0.02 --lifespan 60 --plot --interactive
```

Runs for 60 days, shows the graph each day, and displays a new-infections-per-day bar chart at the end.

---

## Output Files

| File | Produced by |
|---|---|
| `cascade_final.png` | cascade (always) |
| `cascade_activations_per_round.png` | cascade with `--plot` |
| `covid_simulation_plot.png` | covid (always) |
| `covid_infections_per_day.png` | covid with `--plot` |

---

## Model Details

### Cascade (Linear Threshold)

- Nodes start **inactive**; initiator nodes start **active**.
- Each round (synchronous): an inactive node activates if `active_neighbors / total_neighbors >= threshold`.
- Simulation stops when no new nodes activate.
- Reports whether a **full cascade** (all nodes reached) occurred.

### COVID (SIRS with Extensions)

States: **S** (Susceptible) · **I** (Infected) · **R** (Recovered) · **D** (Dead) · **SH** (Sheltered) · **V** (Vaccinated, not yet infected)

| Rule | Detail |
|---|---|
| Vaccination | Vaccinated nodes (V) have `0.25×` infection probability (breakthrough infections possible) |
| Recovery | Nodes recover after 10 days infected |
| Death | After 10 days infected, nodes die with `--probability_of_death` |
| Immunity waning | Unvaccinated recovered: 90 days · Vaccinated never infected: 180 days · Vaccinated + recovered (hybrid): 365 days |
| Shelter | Susceptible nodes with >50% infected neighbors shelter for 14 days with probability `--shelter` |

All state transitions use a start-of-day snapshot (synchronous updates) to prevent same-day chain effects.

---

## Error Handling

- Missing or unreadable GML file → descriptive error message, clean exit
- Empty graph → error message, clean exit
- Missing required parameters (`--initiator`, `--probability_of_infection`) → error message, clean exit
- Initiator nodes not found in graph → warning per node, skips missing nodes
