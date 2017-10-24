# WebCrawler
Crawls URL’s, Computes PageRank of the explored subgraph of web pages using Google’s Algorithm &amp; downloads them.

How to run program ?
Firstly, Navigate to directory where crawler.py is placed using terminal

-> python3 crawler.py searchQuery maxPages maxPagesPerSite crawlMethod

So for eg : 
-> python3 crawler.py knuckle sandwich 1000 10 PR


Input Parameters explained :

searchQuery - Search query containing any number of words separated by space
maxPages - Maximum number of URL's to be crawled by crawler. Can also interrupt the crawler in between using Ctrl + C in terminal and the crawler will generate log for all visited url's before interruption.
maxPagesPerSite -  Imposes a limit on the number of pages to be crawled from the same site.
crawlMethod - BFS or PR for Breadth First Search and Page Rank respectively.

External Modules needed:

pip3 install GoogleScraper
pip3 install url_normalize
pip3 install urllib


1. The crawler fetches starting pages and adds them to pagesToVisit queue. 
2. Pops out the first element from queue, normalizes the url, extracts base URL, performs various checks on the url, parses links from url ,downloads the webpage, filters out and adds links to the queue, computes Page Rank of the currently explored subgraph & sorts the queue accordingly, deals with leaks & sinks, saves all info about the visited url to log and finally, repeats the same process for the next url in queue.
3. Generates a log at the end of crawl with statistics.

Data Structures used in the crawler :

pagesToVisit - A list implemented as a queue containing the pages to be crawled in order of decreasing page ranks for the Page Rank oriented crawler and as a FIFO structure for the BFS oriented crawler respectively.
visited - A list containing visited url’s in the order they were visited.
ranks - A dictionary with url as key and its corresponding page rank as value.
graph - A dictionary with an url as key and a list of its out-linked url’s as value.
numberOfTimesSiteVisited - A dictionary with base url as key and number Of times it has been visited as value. 


The major functions in the crawler and their descriptions are as follows:

startCrawl(searchQuery, maxPages , maxPagesPerSite, crawlMethod , startTime) - Main runner function controlling the crawling.

getTopResultsFromGoogle(searchQuery) - Gets the starting pages from google for the user given search query using a python Module called GoogleScraper.

allowedToVisitByRobot(baseUrl,url) - Checks whether the crawler is allowed to visit the url by parsing the robots.txt file using RobotParser python module. 

getLinks(url) - parses the webpage at url to extract links and also downloads the webpage.

addLinksToPagesToVisitAndGraph(links,pagesToVisit,graph,url) - filters out and adds the links to the pagesToVisit queue.(See special features at bottom for more info.) . Also adds the links to the graph.

computeAndSortRanks(graph,pagesToVisit) - Calculates page ranks using page rank algo, fixes the leaks , and sorts the pagesToVisit queue accordingly.

fixLeaks(graph,ranks) - Deals with the drain of average page rank of graph because of leaks and sinks by implementing tax collection strategy ,collecting 100% from dead ends in the subgraph and 15% from others and redistributes the sum equally among all.

Special features:

-> Implemented PageRank algo which runs in O(n^2).

-> Deals with leaks and sinks in the graph by implementing tax collection & redistribution strategy.

-> Filters url’s based on the criteria that url’s shouldn’t have javascript, jpg, exe, pdf, cgi in them. Also the url should start with http or https and shouldn’t have already been visited or added to pagesToVisit queue.Also it shouldn’t be the same as the url of webpage from which it has been extracted.

-> Normalizes the url’s using url_normalize python module.

-> Parses base Url by extracting scheme and net location from URL using urlparse() in
 urllib module. Base URL is then used to keep track of number times a site has been visited in order to avoid the crawler from becoming too focused on a small number of sites.

-> Used python inbuilt sort method for sorting pagesToVisit list and lambda expression to map each url in pagesToVisit to its corresponding rank for sorting. This is one of the highly efficient ways to sort.
 
-> Logs all HTTP error codes : 404,503 etc. and also logs Timeout. I’ve Set the socket timeout to 2 seconds which means the crawler moves onto next url if no response received within 2 seconds.

-> Checks for Earlier Visits of a url.

-> Exception handling : prints out type, description and line no. Of error if any and moves on to next URL to crawl.

Bugs & Limitations:

-> GoogleScraper sometimes appends ‘url?url=‘ at the beginning of returned start page url’s. I have handled this problem by writing a method to clean the returned results by GoogleScraper and automatically deleting cached pages at the beginning of every crawl.

-> Doesn’t treat 2 effectively same but syntactically different url’s ,one beginning with http & other with https , as same. This sometimes leads to crawler visiting http://www.urbandictionary.com as well as https://urbandictionary.com

-> Page Rank focused crawler becomes slow after a while since the size of graph grows enormously leading to elongated page rank computation time.
