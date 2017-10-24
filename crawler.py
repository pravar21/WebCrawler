import urllib
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
from urllib.parse import urlparse, urljoin
from GoogleScraper import scrape_with_config, GoogleSearchError
import sys
from datetime import datetime
import urllib.robotparser
import os, ssl
import socket
import time
from url_normalize import url_normalize
import shutil

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

socket.setdefaulttimeout(2)

VisitedUrlDictionary = {}
visited = []
AGENT_NAME = 'pravar-web-crawler'

class LinkParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    self.links = self.links + [newUrl]

    def getLinks(self, url, numberVisited, ranks, crawlMethod):
        self.links = []
        self.baseUrl = url

        try:
            response = urlopen(url)
        except urllib.error.HTTPError as e:
            VisitedUrlDictionary[url].append(e.code)
            saveToPRLog(url, ranks) if crawlMethod == 'PR' else saveToBFSLog(url)
            raise
        except: #socket.timeout:
            visited.append(url)
            VisitedUrlDictionary[url].append('Timeout')
            raise

        VisitedUrlDictionary[url].append(response.status)

        if response.status == 200:
            if 'text/html' in response.info()["content-type"]:
                htmlBytes = response.read()
                VisitedUrlDictionary[url].append(len(str(htmlBytes)))

                saveFile = open(str(numberVisited)+'.txt', 'w')
                saveFile.write(str(htmlBytes))
                saveFile.close()
                try:
                    htmlString = htmlBytes.decode("utf-8")
                except:
                    visited.append(url)
                    VisitedUrlDictionary[url].append('Can\'t Decode HTML Page')
                    raise
                self.feed(htmlString)
                return htmlString, self.links[:50]
            else:
                return "",[]

#GoogleScraper Module to fetch results from search engine
def getTopResultsFromGoogle(word):
    keywords = []
    keywords.append(word)

    config = {
        'use_own_ip': 'True',
        'keywords': keywords,
        'search_engines': ['google', ],
        'num_pages_for_keyword': 2,
        'scrape_method': 'http',
        'do_caching': 'False'
    }

    try:
        search = scrape_with_config(config)
    except GoogleSearchError as e:
        print(e)

    results = []
    count = 0

    if search.serps[0].page_number == 2:
        search.serps.reverse()
    for serp in search.serps:
        print(serp)
        for link in serp.links:
            if(count == 10):
                break
            results.append(link.link)
            count += 1

    return results

def saveToBFSLog(url):
    visited.append(url)
    
def saveToPRLog(url,ranks):
    visited.append(url)
    VisitedUrlDictionary[url].append(ranks[url] if url in ranks else 0.15)

def writeToBFSLog(finalRanks,outputLogBFS,totalTime):
    totalFileSize = 0
    total404 = 0
    for url in visited:
        if(len(VisitedUrlDictionary[url])<=2):
            outputLogBFS.write(url + " Time : " + str(VisitedUrlDictionary[url][0] if len(VisitedUrlDictionary[url]) >=1 else ' ') + " Code : " + str(VisitedUrlDictionary[url][1] if len(VisitedUrlDictionary[url]) >=2 else ' ') + " Rank : " + str(finalRanks[url] if url in finalRanks else 0.15) + "\n")
            if VisitedUrlDictionary[url][1] == 404:
                total404 += 1

        else:
            outputLogBFS.write(url + " Time : " + str(VisitedUrlDictionary[url][0] if len(VisitedUrlDictionary[url]) >=1 else ' ') + " Code : " + str(VisitedUrlDictionary[url][1] if len(VisitedUrlDictionary[url]) >=2 else ' ') + " Size : " + str(VisitedUrlDictionary[url][2] if len(VisitedUrlDictionary[url]) >=3 else ' ') + " Rank : " + str(finalRanks[url] if url in finalRanks else 0.15) + "\n")
            totalFileSize += VisitedUrlDictionary[url][2]
            if VisitedUrlDictionary[url][1] == 404:
                total404 += 1

    outputLogBFS.write("\nNo. of Files : " + str(len(visited)))
    outputLogBFS.write("\nTotal Size : " + str(totalFileSize / 1000000) + " MB")
    outputLogBFS.write("\nTotal No. of 404 errors : " + str(total404))
    outputLogBFS.write("\nTotal Time for crawling : " + str(totalTime / 60) + " minutes")
    outputLogBFS.close()

def writeToPRLog(finalRanks,outputLogPR,totalTime):
    totalFileSize = 0
    total404 = 0
    for url in visited:
        if(len(VisitedUrlDictionary[url])<=3):
            outputLogPR.write(url + " Time : " + str(VisitedUrlDictionary[url][0] if len(VisitedUrlDictionary[url]) >=1 else ' ') + " Code : " + str(VisitedUrlDictionary[url][1] if len(VisitedUrlDictionary[url]) >=2 else ' ') + " RankAtCrawl: " + str(VisitedUrlDictionary[url][2] if len(VisitedUrlDictionary[url]) >=3 else ' ') + " FinalRank : " + str(finalRanks[url] if url in finalRanks else 0.15) + "\n")
            if VisitedUrlDictionary[url][1] == 404:
                total404 += 1
        else:
            outputLogPR.write(url + " Time : " + str(VisitedUrlDictionary[url][0] if len(VisitedUrlDictionary[url]) >=1 else ' ') + " Code : " + str(VisitedUrlDictionary[url][1] if len(VisitedUrlDictionary[url]) >=2 else ' ') + " Size : " + str(VisitedUrlDictionary[url][2] if len(VisitedUrlDictionary[url]) >=3 else ' ')+" RankAtCrawl: "+ str(VisitedUrlDictionary[url][3] if len(VisitedUrlDictionary[url]) >=4 else ' ') + " FinalRank : " + str(finalRanks[url]if url in finalRanks else 0.15) + "\n")
            totalFileSize += VisitedUrlDictionary[url][2]
            if VisitedUrlDictionary[url][1] == 404:
                total404 += 1

    outputLogPR.write("\nNo. of Files : " + str(len(visited)))
    outputLogPR.write("\nTotal Size : " + str(totalFileSize/1000000) + " MB")
    outputLogPR.write("\nTotal No. of 404 errors : " + str(total404))
    outputLogPR.write("\nTotal Time for crawling : " + str(totalTime/60) + " minutes")
    outputLogPR.close()

def calculatePageRanks(graph):
    d = 0.85
    numloops = 10
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) #/ npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * ranks[node] / len(graph[node])
            newranks[page] = newrank
            ranks[page] = newranks[page]
        ranks = newranks
    return ranks

def fixLeaks(graph,ranks):
    taxCollected = 0.0

    for node in graph:
        if not graph[node]:
            taxCollected += ranks[node]
        else:
            taxCollected += 0.15 * ranks[node]
    for url in ranks:
        ranks[url] += (taxCollected / len(ranks))

def initializeRanksAndGraphForTopResultsFromGoogle(startingPages,graph):
    ranks = {}
    for page in startingPages:
        ranks[page] = 1 / (len(startingPages))
        graph[page] = []
    return ranks

def allowedToVisitByRobot(baseUrl,url):

    try:
        #if baseUrl:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(urljoin(baseUrl, 'robots.txt'))
        try:
            parser.read()
        except:
            return True
        return parser.can_fetch(AGENT_NAME, url)

        #else:
            #return False
    except:
        return True


def addLinksToPagesToVisitAndGraph(links,pagesToVisit,graph,url):

    for link in links:
        link = url_normalize(link, charset='utf-8')
        parsedUrl = urlparse(link)

        if parsedUrl.scheme != 'http' and parsedUrl.scheme != 'https':
            continue

        if link not in pagesToVisit and link not in visited and 'cgi' not in link and \
                        'javascript' not in link and 'jpg' not in link and 'pdf' not in link and 'exe' not in link and link != url\
                        and (link.startswith('http') or link.startswith('https')):
            pagesToVisit.append(link)
            graph[link] = []
            if url not in graph:
                graph[url] = [link]
            else:
                graph[url].append(link)

def computeAndSortRanks(graph,pagesToVisit):

    ranks = calculatePageRanks(graph)
    fixLeaks(graph,ranks)
    pagesToVisit.sort(key=lambda k: ranks[k], reverse=True)
    return ranks

def cleanResults(pagesToVisit):
    for i in range(0,len(pagesToVisit)):
        httpStartIndex = pagesToVisit[i].find('http')
        pagesToVisit[i] = pagesToVisit[i][httpStartIndex:]

def startCrawl(searchQuery, maxPages , maxPagesPerSite, crawlMethod , startTime):
    graph = {}
    numberOfTimesSiteVisited = {}
    numberOfSitesEncountered = 0
    parser = LinkParser()
    pagesToVisit = getTopResultsFromGoogle(searchQuery)
    cleanResults(pagesToVisit)

    ranks = initializeRanksAndGraphForTopResultsFromGoogle(pagesToVisit,graph)
    numberVisited = 0

    while numberVisited < maxPages and pagesToVisit:
        url = pagesToVisit[0]
        url = url_normalize(url,charset='utf-8')
        parsedUrl = urlparse(url)
        baseUrl = parsedUrl.scheme+"://"+parsedUrl.netloc+"/"
        if not baseUrl.startswith('http') and not baseUrl.startswith('https'):
            pagesToVisit = pagesToVisit[1:]
            continue
        if baseUrl in numberOfTimesSiteVisited:
            numberOfTimesSiteVisited[baseUrl] += 1
        else:
            numberOfTimesSiteVisited[baseUrl] = 1

        numberOfSitesEncountered += 1
        pagesToVisit = pagesToVisit[1:]
        try:
            if numberOfTimesSiteVisited[baseUrl] <= maxPagesPerSite and 'cgi' not in url and 'javascript' not in url \
                    and 'jpg' not in url and 'pdf' not in url and 'exe' not in url:

                if allowedToVisitByRobot(baseUrl,url):
                    print(numberVisited + 1, "Visiting:", url)
                    numberVisited += 1
                    VisitedUrlDictionary[url] = [datetime.now().time()]
                    data, links = parser.getLinks(url,numberVisited,ranks,crawlMethod)
                    addLinksToPagesToVisitAndGraph(links,pagesToVisit,graph,url)

                    if crawlMethod == 'PR':
                        ranks = computeAndSortRanks(graph,pagesToVisit)
                        print("Crawled", url, "at time :", VisitedUrlDictionary[url][0],
                              "with return code: ", VisitedUrlDictionary[url][1], "& size: ",
                              VisitedUrlDictionary[url][2] if len(VisitedUrlDictionary[url]) >= 3 else 'Not Downloaded',
                              " Rank : ", ranks[url] if url in ranks else 'Not Assigned')
                    else:
                        print("Crawled", url, "at time :", VisitedUrlDictionary[url][0],
                           "with return code: ", VisitedUrlDictionary[url][1], "& size: ", VisitedUrlDictionary[url][2] if len(VisitedUrlDictionary[url]) >=3 else 'Not Downloaded')

                    saveToPRLog(url,ranks) if crawlMethod == 'PR' else saveToBFSLog(url)

        except KeyboardInterrupt:
            writeToPRLog(ranks, open('output_PR.txt', 'w'), time.time() - startTime) if crawlMethod == 'PR' else writeToPRLog(ranks, open('output_BFS.txt', 'w'),time.time() - startTime)
            raise

        except:
            print("Error :")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno)

    if crawlMethod == 'BFS':
        ranks = calculatePageRanks(graph)

    return ranks

if __name__ == "__main__":
    try:
        shutil.rmtree('.scrapecache')
        os.remove('google_scraper.db')
    except:
        pass
    queryString = ""
    for word in sys.argv[1:-3]:
        queryString += word + " "

    queryString = queryString.strip()

    startTime = time.time()

    finalRanks = startCrawl(queryString, int(sys.argv[-3]), int(sys.argv[-2]), sys.argv[-1].upper(),startTime)

    totalTime = time.time() - startTime

    if sys.argv[-1].upper() == 'PR':
        writeToPRLog(finalRanks,open('output_PR.txt', 'w'), totalTime)
    else:
        writeToBFSLog(finalRanks,open('output_BFS.txt', 'w'), totalTime)

