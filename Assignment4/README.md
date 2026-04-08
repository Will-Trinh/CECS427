# Market Clearing Graph Program
CECS 427 – Assignment 4
Oanh Tran (029661786)
William Trinh (030650397)

### Description:
This program reads a bipartite graph from a .gml file and computes a market-clearing matching between buyers and sellers. It iteratively adjusts seller prices until all buyers are matched. Optional features include graph visualization and step-by-step interactive output.

### Setup:
Install required libraries:

pip install networkx matplotlib

### How to Run:

python market_strategy.py input_file.gml --plot --interactive

Optional Flags:

--plot        Display the graph
--interactive Show step-by-step execution

### Examples:

python market_strategy.py example.gml --plot

python market_strategy.py example.gml --interactive

python market_strategy.py example.gml --plot --interactive
