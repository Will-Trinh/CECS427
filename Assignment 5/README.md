# Assignment 5 - Web Crawling and PageRank

**CECS 427**
Oanh Tran 029661786 | William Trinh 030650397

## Dependencies

Install required packages:

```
pip install scrapy networkx matplotlib
```

## Usage

```
python ./page_rank.py [--crawler FILE] [--input FILE] [--loglogplot] [--crawler_graph FILE] [--pagerank_values FILE]
```

### Parameters

| Parameter | Description |
|---|---|
| `--crawler FILE` | Crawl the web using seed URLs in FILE and build a directed graph |
| `--input FILE` | Load an existing graph from a `.gml` file |
| `--loglogplot` | Generate a log-log plot of the degree distribution |
| `--crawler_graph FILE` | Save the crawled graph to FILE (default: `out_graph.gml`) |
| `--pagerank_values FILE` | Write PageRank scores for all nodes to FILE |

### Crawler file format

```
<max_nodes>
<domain_url>
<start_url_1>
<start_url_2>
...
```

Example (`crawler.txt`):
```
100
https://dblp.org/pid
https://dblp.org/pid/e/PErdos.html
https://dblp.org/pid/s/PaulGSpirakis.html
https://dblp.org/pid/89/8192.html
```

## Examples

Crawl the web, run PageRank, save the graph, generate a log-log plot, and write rank values:
```
python ./page_rank.py --crawler crawler.txt --loglogplot --crawler_graph out_graph.gml --pagerank_values node_rank.txt
```

Load an existing graph, run PageRank, and generate a log-log plot:
```
python ./page_rank.py --input graph.gml --loglogplot --pagerank_values node_rank.txt
```

Load an existing graph and run PageRank only:
```
python ./page_rank.py --input graph.gml --pagerank_values node_rank.txt
```

## Output

- **`out_graph.gml`** (or name specified by `--crawler_graph`) — the crawled directed graph in GML format
- **`node_rank.txt`** (or name specified by `--pagerank_values`) — PageRank score for each node
- **`loglog_degree_distribution.png`** — saved log-log plot image (when `--loglogplot` is used)
