import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin
import networkx as nx


# File extensions to skip (not HTML pages)
SKIP_EXTENSIONS = (
    ".tar", ".gz", ".zip", ".bz2", ".xz", ".7z",
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac",
    ".css", ".js", ".json", ".xml", ".rdf", ".nt", ".ttl",
    ".exe", ".dmg", ".rpm", ".deb", ".iso",
    ".csv", ".tsv", ".dat", ".bin", ".nq",
)

# Max new links to follow per page which keeps the graph following more links
# preventing crawler forming star graph
LINKS_PER_PAGE = 5


class PageSpider(scrapy.Spider):
    name = "pageSpider"

    custom_settings = {
        "LOG_LEVEL": "INFO",
        "DEPTH_LIMIT": 10,
        "CONCURRENT_REQUESTS": 4,
        "DOWNLOAD_DELAY": 0.5,
        "RETRY_TIMES": 1,
        "DOWNLOAD_TIMEOUT": 15,
        "DOWNLOAD_MAXSIZE": 10 * 1024 * 1024,
        "ROBOTSTXT_OBEY": False,
        "USER_AGENT": "Mozilla/5.0 (compatible; StudentBot/1.0)",
        "HTTPERROR_ALLOWED_CODES": [],
        "MEDIA_ALLOW_REDIRECTS": True,
        "AJAXCRAWL_ENABLED": False,
        "DOWNLOADER_CLIENT_TLS_VERIFY": False,
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",
    }

    def __init__(self, startUrlsList, allowedDomain, maxNodes, outputFile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = startUrlsList
        self.allowedDomain = allowedDomain
        self.maxNodes = maxNodes
        self.outputFile = outputFile
        self.directedGraph = nx.DiGraph()
        self.visitedPages = set()

    def hasCapacity(self):
        return self.directedGraph.number_of_nodes() < self.maxNodes

    def isHtmlUrl(self, url):
        """Check if the URL likely points to an HTML page."""
        pathLower = urlparse(url).path.lower()
        for ext in SKIP_EXTENSIONS:
            if pathLower.endswith(ext):
                return False
        return True

    def filterLink(self, rawLink, currentUrl):
        fullUrl = urljoin(currentUrl, rawLink)
        fullUrl = fullUrl.split("#")[0]

        if not fullUrl or fullUrl.startswith(("javascript:", "mailto:", "tel:")):
            return None

        parsedUrl = urlparse(fullUrl)
        if self.allowedDomain not in parsedUrl.netloc:
            return None
        if parsedUrl.scheme not in ("http", "https"):
            return None
        if not self.isHtmlUrl(fullUrl):
            return None

        return fullUrl

    def parse(self, response):
        contentType = response.headers.get("Content-Type", b"").decode("utf-8", errors="ignore")
        if "text/html" not in contentType:
            return
        currentUrl = response.url
        if not self.hasCapacity() and not self.directedGraph.has_node(currentUrl):
            return

        self.visitedPages.add(currentUrl)
        if not self.directedGraph.has_node(currentUrl):
            self.directedGraph.add_node(currentUrl)

        extractedLinks = response.css("a::attr(href)").getall()

        # Track how many NEW pages we schedule from this page
        followedCount = 0

        for rawLink in extractedLinks:
            fullUrl = self.filterLink(rawLink, currentUrl)
            if fullUrl is None:
                continue

            # Always record edges between existing nodes
            if self.directedGraph.has_node(fullUrl):
                self.directedGraph.add_edge(currentUrl, fullUrl)
                continue

            # For new nodes: check capacity and per-page limit
            if not self.hasCapacity():
                continue
            if followedCount >= LINKS_PER_PAGE:
                continue

            # Add the new node and edge
            self.directedGraph.add_edge(currentUrl, fullUrl)
            followedCount += 1

            # Schedule crawl if not visited yet
            if fullUrl not in self.visitedPages:
                yield scrapy.Request(
                    fullUrl,
                    callback=self.parse,
                    errback=self.handleError,
                    dont_filter=False,
                )

    def handleError(self, failure):
        self.logger.warning(f"Request failed: {failure.request.url}")

    def closed(self, reason):
        nx.write_gml(self.directedGraph, self.outputFile)
        self.logger.info(f"Graph saved to {self.outputFile}")
        self.logger.info(
            f"Nodes: {self.directedGraph.number_of_nodes()}, "
            f"Edges: {self.directedGraph.number_of_edges()}"
        )

#saves to gml file
def runSpider(filename, outputFile = "out_graph.gml"):
    maxNodes, allowedDomain, startUrlsList = parseCrawlerFile(filename)
    print(f"Crawling domain: {allowedDomain}")
    print(f"Max nodes: {maxNodes}")
    print(f"Start URLs: {startUrlsList}")
    crawlerProcess = CrawlerProcess()
    crawlerProcess.crawl(
        PageSpider,
        startUrlsList=startUrlsList,
        allowedDomain=allowedDomain,
        maxNodes=maxNodes,
        outputFile=outputFile,
    )
    crawlerProcess.start()


def parseCrawlerFile(filePath):
    with open(filePath, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    maxNodes = int(lines[0])
    domainUrl = lines[1]
    parsedDomain = urlparse(domainUrl)
    allowedDomain = parsedDomain.netloc if parsedDomain.netloc else domainUrl

    startUrlsList = lines[2:]
    return maxNodes, allowedDomain, startUrlsList

