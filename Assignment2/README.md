# Assignment 2 — Social and Large-Scale Networks

**Authors:** Oanh Tran (029661786), William Trinh (030650397)  
**Course:** CECS 427

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- Required packages:

```bash
pip install networkx matplotlib scipy
```

### Files
| File | Description |
|------|-------------|
| `graph_analysis.py` | Main analysis program |
| `sample_graph.gml` | Sample graph with node `color` and edge `sign` attributes |
| `sample_events.csv` | Sample CSV for temporal simulation |
| `README.md` | This file |

---

## Usage

### General Syntax

```bash
python graph_analysis.py --input <graph_file.gml> [OPTIONS]
```

### Available Options

| Flag | Description |
|------|-------------|
| `--input FILE` | **(Required)** Input `.gml` graph file |
| `--components n` | Partition graph into `n` components using Girvan-Newman |
| `--split_output_dir` | Export each component as a separate `.gml` file |
| `--plot [C\|N\|P]` | Visualization: **C**=clustering, **N**=overlap, **P**=attributes |
| `--verify_homophily` | Run t-test for homophily on node `color` attribute |
| `--verify_balanced_graph` | Check if signed graph is structurally balanced (BFS) |
| `--simulate_failures k` | Remove `k` random edges and analyze network impact |
| `--robustness_check k` | Run multiple `k`-edge failure simulations before partitioning |
| `--temporal_simulation FILE` | Load CSV of edge events and animate graph evolution |
| `--output [FILE]` | Save final graph to `.gml` (default: `outputFinal.gml`) |

---

## Sample Commands

### Partition into 3 components, plot clustering, and export
```bash
python graph_analysis.py --input sample_graph.gml --components 3 --plot C --output output.gml
```

### Verify homophily and structural balance
```bash
python graph_analysis.py --input sample_graph.gml --verify_homophily --verify_balanced_graph --output output.gml
```

### Simulate 5 random edge failures
```bash
python graph_analysis.py --input sample_graph.gml --simulate_failures 5
```

### Robustness check before partitioning
```bash
python graph_analysis.py --input sample_graph.gml --components 3 --robustness_check 3 --output output.gml
```

### Run temporal simulation from CSV
```bash
python graph_analysis.py --input sample_graph.gml --temporal_simulation sample_events.csv --output output.gml
```

### Full pipeline
```bash
python graph_analysis.py --input sample_graph.gml --components 3 --robustness_check 2 --split_output_dir --plot C --simulate_failures 5 --verify_homophily --verify_balanced_graph --temporal_simulation sample_events.csv --output output.gml
```

---

## Approach & Methodology

### Graph Loading
- Uses `networkx.read_gml()` to load `.gml` files with full node/edge attribute support.
- Validates input file existence and format, printing clear error messages on failure.

### Clustering Coefficient (`--plot C`)
- Computed via `networkx.clustering()` for each node.
- Visualized as **node size** (larger = higher CC), with **node color** mapped to degree.
- A color bar indicates the degree scale.

### Neighborhood Overlap (`--plot N`)
- For each edge `(u, v)`, overlap = `|N(u) ∩ N(v)| / |N(u) ∪ N(v)|`.
- Visualized as **edge thickness** (thicker = higher overlap), with **edge color** mapped to `deg(u) + deg(v)`.
- Edge labels display the computed overlap value.

### Community Partitioning (`--components n`)
- Implements the **Girvan-Newman algorithm**: iteratively removes the edge with the highest betweenness centrality until the desired number of connected components is reached.
- Each step prints the removed edge, its betweenness score, and the current component state.

### Homophily Verification (`--verify_homophily`)
- Tests whether nodes preferentially connect to same-`color` neighbors.
- For each node, computes the fraction of neighbors sharing its color attribute.
- The **expected fraction** under a null model (random assignment) is `Σ p_c²` where `p_c` is each color's proportion.
- A **one-sample t-test** compares observed vs. expected fractions.
- Reports t-statistic, p-value, and whether homophily or heterophily is detected (α = 0.05).

### Structural Balance (`--verify_balanced_graph`)
- Uses **BFS-based 2-coloring** on signed edges.
- Positive (`+`) edges indicate "same group" constraints; negative (`-`) edges indicate "different group."
- Attempts to assign all nodes to two groups consistently. If a contradiction is found, the graph is **not balanced**.
- Reports the partition groups if balanced, or the violating edge if not.

### Simulate Failures (`--simulate_failures k`)
- Randomly removes `k` edges from the graph.
- Reports: change in **average shortest path length**, new **connected components**, and a full **edge betweenness centrality** comparison (before vs. after).

### Robustness Check (`--robustness_check k`)
- Runs 10 independent trials of removing `k` random edges.
- Aggregates: average number of components, min/max component sizes, change in average shortest path, and whether original cluster structure persists (≥90% overlap threshold).

### Temporal Simulation (`--temporal_simulation file.csv`)
- Loads a CSV file with columns: `source`, `target`, `timestamp`, `action` (`add`/`remove`).
- Processes events in timestamp order and **animates** the graph evolution using `matplotlib`.
- Newly added edges are highlighted in green. Each frame displays current node/edge counts and number of components.

### Attribute Handling
- If node `color` or edge `sign` attributes are missing when needed, the program warns the user and assigns **random defaults** so analysis can still proceed.
- This ensures graceful handling of graphs without pre-set attributes.

### Output
- `--output` saves the final graph state (after all modifications) to a `.gml` file.
- `--split_output_dir` exports each connected component as a separate `.gml` file (`component_1.gml`, `component_2.gml`, etc.).

---

## Sample Input Files

### `sample_graph.gml`
A 12-node signed graph with 3 color groups (red, blue, green). Intra-group edges are positive (`+`), inter-group edges are negative (`-`), with one deliberately unbalanced edge to demonstrate the balance checker.

### `sample_events.csv`
A 17-event temporal sequence of edge additions and removals across 10 timestamps, suitable for testing the temporal simulation animation.
