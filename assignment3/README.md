# Assignment 3: Game Theory – Traffic Analysis

**CECS 427**  
Oanh Tran (029661786) & William Trinh (030650397)

## Description

This program reads a directed graph from a `.gml` file where each edge has polynomial cost parameters `a` and `b` (representing the cost function `c(x) = a·x + b`). Given a number of vehicles and source/destination nodes, it computes:

- **Social Optimum** – the flow assignment that minimizes total travel cost across all vehicles.
- **Travel Equilibrium (Nash Equilibrium)** – the flow assignment where no individual driver can reduce their cost by switching routes (computed via Rosenthal's potential).

## Requirements

- Python 3.6+
- NetworkX (`pip install networkx`)
- Matplotlib (`pip install matplotlib`)

## Usage

```
python traffic_analysis.py <gml_file> <num_vehicles> <start_node> <end_node> [--plot]
```

### Parameters

| Parameter        | Description                                      |
|------------------|--------------------------------------------------|
| `gml_file`       | Path to the directed graph file in GML format    |
| `num_vehicles`   | Number of vehicles in the network                |
| `start_node`     | Starting node ID (integer)                       |
| `end_node`       | Destination node ID (integer)                    |
| `--plot`         | (Optional) Display the graph and edge cost plots |

### Example

```
python traffic_analysis.py traffic.gml 4 0 3 --plot
```

This reads the directed graph in `traffic.gml` and computes the Social Optimum and Travel Equilibrium for 4 vehicles traveling from node 0 to node 3, then displays the graph and polynomial plots.

## GML File Format

Each edge must have attributes `a` and `b` defining its cost polynomial `c(x) = a·x + b`:

```
graph [
  directed 1
  node [ id 0  label "0" ]
  node [ id 1  label "1" ]
  edge [ source 0  target 1  a 1  b 0 ]
]
```

## Error Handling

The program handles the following edge cases:
- Non-existent or unreadable graph files
- Start or end nodes not present in the graph
- Negative number of vehicles
- Undirected graphs (requires a directed graph)
