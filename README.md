#### Oanh Tran:  029661786
#### William Trinh:  030650397
# CECS 427 -- Assignment 1: Graph.py


`graph.py` is a command-line Python program that works with **undirected graphs** using **NetworkX**. It can:

- Generate a random graph using an Erdős–Rényi-style probability 
- Run **Breadth-First Search (BFS)** from one or more starting nodes
- Print a readable BFS tree for each BFS run
- Analyze graph structure (components, cycles, isolated nodes, density, shortest paths if connected)
- Visualize the graph using Matplotlib
  

## Libraries 
- networkx
- matplotlib
- argparse
- collections.deque
- math
- random
  
## Usage Instructions
1. install required libraries
   ```bash
   pip install networkx matplotlib
3. For further detailed usage instructions, run:
   python ./graph.py --help
5. Run program using terminal or command prompt

Command line structure: 

python ./graph.py [--input graph_file.gml] [--create_random_graph n c] [--multi_BFS a1 a2 ...] [--analyze] [--plot] [--output out_graph_file.gml]
- n: integer for number of nodes
- c: a positive integer or float
- a1, a2, ... one or more nodes to perform BFS



## Implementation

**Graph input/Output**
- Graphs are loaded from .gml files using read_graph_file(file) and exported using output_graph(G, file, bfs_results=None).
- During export, the graph is enriched with node attributes:
  - component_id: ID of the connected component the node belongs to
  - is_isolated: indicates whether the node is isolated
- If BFS is performed:
  - bfs_<source>_distance: shortest-path distance from the BFS source
  - bfs_<source>_parent: parent node in the BFS tree
- BFS distances are computed by compute_distances(parent_dict, source), which reconstructs path lengths by tracing parent pointers back to the source.

The program uses `argparse` to define these command-line options:

 `--create_random_graph n c`  `--multi_BFS a1 a2 ...` (a1, a2 ... are node labels) 
 `--analyze` `--plot`  `--input FILE`  - `--output FILE` 

**Generate Random Graph** using the **Erdos-Renyi model** -> generate_graph(n: int, c: float):
- n = # of nodes, c = positive constant 
- creates an undirected graph using networkx library, nx.Graph()
- nodes are added and labeled as strings "0", "1",..."n-1"
- edge probability: p = (c * ln(n))/n
- for each node pair (i, j) where i < j, a random number is generated and if random.random() < p, an edge is added between both nodes
- prints node labels, node pairs with edges, number of nodes and number of edges


**BFS traversal:** -> bfs(graph, start): 
- implements BFS algorithm and uses a queue to explore nodes level by level. A set tracks visited nodes, and a dictionary stores parent-child relationships, used for forming the BFS tree.
- prints the order in which nodes are visited and returns parent dictionary

**BFS Tree Visualuzation** -> draw_bfs_tree(parent, start) and print_bfs_tree(parent, start)
- converts the parent map into a directed graph (nx.DiGraph) and lays nodes out by BFS level (distance). It saves an image bfs_tree_<source>.png and also displays it.
- prints a readable BFS structure in terminal to add on

**Multi-Source BFS** -> multiBFS(G, *start_nodes):
- allows BFS to be executed from multiple starting nodes
- loops through all user-provided nodes, validates that each exists in the graph, and stores results in a dictionary

**Analysis** -> analysis(G):
-  counts of nodes and edges
- connected components: counts and lists connected components
- isolated nodes: identifies and prints nodes with a degree of 0
- cycle detection: detects whether a cycle exists and prints which nodes are in a cycle
- graph density: existing edges/maximum possible edges
- average shortest path length: if graph is not connected, the average shortest path is computed on the largest component. 

**Graph Visualization** -> plot(G) 
- produces a single combined visualization saved as saved as graph_visualization.png.
- utilizes a legend and symbology to distinguish normal nodes, isolated nodes and BFS source nodes and tree edges from one another.
- Draws edges in a light style first (thin gray), then overlays BFS tree edges in distinct colors if BFS results exist.
- Nodes are styled by role:
  - Normal nodes: green circles
  - Isolated nodes: red squares
  - BFS source nodes: gold circles with black outlines

**Main**
- parses command-line arguments, initializes or loads a graph, and conditionally executes BFS traversal, - analysis, visualization, and output based on user-specified options.
  
Command Line → Argument Parsing (argparse) → Parsed Arguments → Graph Input / Generation → BFS Traversal/Visualization → Graph Analysis → Visualization → Graph Export

## Example Commands and Outputs

 `python graph.py --create_random_graph 25 0.8 --multi_BFS 0 5 20 --analyze --plot --output final_graph.gml`

**Erdős–Rényi Graph Generation:**

<img src="https://github.com/user-attachments/assets/a2c7972c-0a2d-40ef-bd5a-4180288c6e6c" width="420" />

**Multi BFS:**

<p align="center">
  <img src="https://github.com/user-attachments/assets/42767e02-0ef2-4817-ae2d-62aa503a44c9" width="420" />
  <img src="https://github.com/user-attachments/assets/e89d440a-72c9-457a-bb05-6f539f53c005" width="420" />
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/ddb0efcb-15be-4303-ba4e-7d1df0e3c278" width="420" />
  <img src="https://github.com/user-attachments/assets/d4a3ba05-27f2-4f2e-8b7b-b0a9a077bff6" width="420" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/15fa3970-1089-43aa-99a6-7d77058dfd05" width="420" />
  <img src="https://github.com/user-attachments/assets/378ddc71-106c-4045-8301-cfa4b12d41de" width="420" />
</p>

**Analysis:**

<img width="2585" height="1070" alt="image" src="https://github.com/user-attachments/assets/e8ff7176-934a-42f0-8cb1-7bf684e68776" />


**Visualization/Graph Export:**

<img width="3456" height="2160" alt="image" src="https://github.com/user-attachments/assets/c6fede14-59c7-41ef-a698-8c67f61a526a" />

------------------------------------------------------------------------------------------------------------
**Connected Graph:**
 `python ./graph.py --create_random_graph 5 8 --multi_BFS 0  --analyze --plot`
 
 **Erdős–Rényi Graph Generation:**
 
<p align="center">
  <img src="https://github.com/user-attachments/assets/a2dbd6b3-d837-4a14-9e51-72b811f8c33b" width="380" />
</p>


**Multi BFS:**

<<p align="center">
  <img src="https://github.com/user-attachments/assets/1d82c607-6d8f-4488-9356-62cd6c63335e" width="420" />
  <img src="https://github.com/user-attachments/assets/bed40955-ebf3-4324-a386-63653ba13d25" width="420" />


**Analysis:**

<p align="center">
  <img src="https://github.com/user-attachments/assets/cc012091-fea6-4b05-9de0-d9b204c8549a" width="700" />
</p>


**Visualization:**

<p align="center">
  <img src="https://github.com/user-attachments/assets/996a8844-8a7d-451a-9dde-4b9075a87e80" width="700" />
</p>

-------------------------------------------------------------------------------------------------------------

**Loading an existing gml using --input**

 `python ./graph.py --input sample.gml  --multi_BFS 1 2  --analyze --plot `


 **Loading GML File**
 
<img width="2063" height="158" alt="image" src="https://github.com/user-attachments/assets/78b045de-6b5e-46aa-b906-df0be9dc2c49" />

**Multi BFS:**
<p align="center">
  <img
    src="https://github.com/user-attachments/assets/f8bba80d-8c6e-4f1a-b2dd-06cab427b7f1"
    width="450"
  />
</p>

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/4f6eafdd-7785-4f80-9664-b3e26cd1b1df"
    width="450"
  />
</p>


<p align="center">
  <img
    src="https://github.com/user-attachments/assets/f8bba80d-8c6e-4f1a-b2dd-06cab427b7f1"
    width="700"
  />
</p>

**Visualization:**

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/4f6eafdd-7785-4f80-9664-b3e26cd1b1df"
    width="700"
  />
</p>


-------------------------------------------------------------------------------------------------------------

**Invalid Command: Missing Args**

`python ./graph.py --create_random_graph  --multi_BFS 0  --analyze --plot`

<img
  src="https://github.com/user-attachments/assets/837ede92-e057-49e8-8221-9a9cbe3f9f5c"
  alt="image"
  style="display:block; margin: 0 auto;"
/>

-------------------------------------------------------------------------------------------------------------
**Non-Existent Node Value for multi_bfs**

`python ./graph.py --create_random_graph 7 1  --multi_BFS 12 6  --analyze --plot`


<p align="center">
  <img src="https://github.com/user-attachments/assets/b7492bbd-de55-4b59-a022-aaa952a0dda8" />
</p>



