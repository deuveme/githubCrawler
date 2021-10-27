import json
import sys
import requests
import random
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Types available in this Github Crawler
VALID_TYPES = ['Repositories', 'Issues', 'Wikis']

# Crawler configuration values
DEFAULT_CONNECTION_ATTEMPTS = 20

# Variables for the search:
GITHUB_SEARCH_URL = 'https://github.com/search?q='
GITHUB_URL = 'https://github.com'
CLASS_TO_SEARCH = {
    'Repositories': 'v-align-middle',
    'Issues': 'Link--muted text-bold',
    'Wikis': 'Link--muted text-small text-bold',
    'CheckIfThereIsResultRepositoryAndWiki': 'd-flex flex-column flex-md-row flex-justify-between border-bottom pb-3 position-relative',
    'CheckIfThereIsResultIssue': 'd-flex flex-column flex-md-row flex-justify-between border-bottom color-border-muted pb-3 position-relative',
    'Stats': 'd-inline'
}


class GithubCrawler:
    """  GitHub crawler that implements the GitHub search and returns all the links from the search result """

    def __init__(self, inputFileLink, attempts=DEFAULT_CONNECTION_ATTEMPTS, print_info=False):
        """ Init function for the class.

        Attributes:
            inputFileLink: Input file link.
            attempts: Number of attempts in case of connection error.
        """

        with open(inputFileLink, encoding="utf8") as unparsedInputFile:
            inputJSON = json.load(unparsedInputFile)

        if 'keywords' not in inputJSON or not inputJSON['keywords']:
            raise self.KeyWordNotValid
        if 'proxies' not in inputJSON or not inputJSON['proxies']:
            raise self.ProxyNotValid
        if 'type' not in inputJSON or inputJSON['type'] not in VALID_TYPES:
            raise self.TypeNotValid

        self.keywords = inputJSON['keywords']
        self.proxies = [{"http": 'http://' + proxy, "https": 'https://' + proxy} for proxy in inputJSON['proxies']]
        self.type = inputJSON['type']
        self.totalAttempts = attempts
        self.print_info = print_info

    class TypeNotValid(Exception):
        """Exception raised for errors in the Type.

        Attributes:
            message: explanation of the error
        """

        def __init__(self, message="Type not valid. Has to be: " + str(VALID_TYPES)):
            self.message = message
            super().__init__(self.message)

    class KeyWordNotValid(Exception):
        """Exception raised for errors in the Keyword.

        Attributes:
            message: explanation of the error
        """

        def __init__(self, message="Keyword missing."):
            self.message = message
            super().__init__(self.message)

    class ProxyNotValid(Exception):
        """Exception raised for errors in the Proxy.

        Attributes:
            message: explanation of the error
        """

        def __init__(self, message="Proxy missing."):
            self.message = message
            super().__init__(self.message)

    class DataNotFoundException(Exception):
        """Exception raised for errors in the Soup Search.

        Attributes:
            message: explanation of the error
        """

        def __init__(self, message="Data not found. Github HTML may have changed."):
            self.message = message
            super().__init__(self.message)

    def getOwner(self, link):
        """ This function gets the owner of the repository link.

        Attributes:
            link: valid URL of a repository.
        Output: User of the owner.
        """

        owner, _, _ = link[1:].partition('/')
        return owner

    def getLanguageStats(self, link):
        """ This function gets the languages stats of the repository link.

        Attributes:
            link: valid URL of a repository.
        Output: Languages stats of the repository.
        """

        stats = {}
        attempts = 0
        while True:
            try:
                languages = BeautifulSoup(self.downloadHTML(link), 'html.parser'). \
                    find_all("li", {"class": CLASS_TO_SEARCH['Stats']})
                if len(languages) > 0:
                    for language in languages:
                        spans = language.find_all("span")
                        if len(spans) == 2:
                            stats[spans[0].text] = spans[1].text[:-1]
                        else:
                            stats[spans[1].text] = spans[2].text[:-1]
                    return stats
                else:
                    return 'Not data about languages'

            except requests.exceptions.RequestException:
                attempts += 1
                if attempts == self.totalAttempts:
                    if self.print_info:
                        print("FAIL after " + str(self.totalAttempts) + " attempts.")
                    return {
                        'error': str(sys.exc_info()[1])
                    }

    def getRepositoryInfoWithExtra(self, link):
        """ This function extract the info of a link repository.

        Attributes:
            link: valid github URL without 'https://github.com', i.e. /qiyuangong/leetcode
        Output: Info of the repository.
        """

        if self.print_info:
            print("Creating link to repository: " + GITHUB_URL + link)
        return [
            {"url": GITHUB_URL + link,
             "extra": {
                 "owner": self.getOwner(link),
                 "language_stats": self.getLanguageStats(GITHUB_URL + link)
             }
             }]

    def downloadHTML(self, link):
        """ This function download the HTML of the URL.

        Attributes:
            link: valid URL.
        Output: HTML text of the page.
        """

        return requests.get(link, proxies=self.proxies[random.randint(0, len(self.proxies) - 1)]).text

    def getURLs(self, html):
        """ This function extract the URLs of the HTML.

        Attributes:
            html: valid HTML text.
        Output: List of URL.
        """

        result = []
        soup = BeautifulSoup(html, 'html.parser')
        soupFound = soup.find_all("a", {"class": CLASS_TO_SEARCH[self.type]})
        if len(soupFound) != 0:
            if self.type == 'Repositories':
                with ThreadPoolExecutor() as executor:
                    canContinue = True
                    fase = []
                    for i in range(0, len(soupFound)):
                        if canContinue:
                            if soupFound[i].get('href'):
                                fase.append(executor.submit(self.getRepositoryInfoWithExtra, soupFound[i].get('href')))
                            else:
                                canContinue = False
                        else:
                            break
                    if not canContinue:
                        raise self.DataNotFoundException
                    else:
                        result = [f.result()[0] for f in as_completed(fase)]
            else:
                for i in range(0, len(soupFound)):
                    if soupFound[i].get('href'):
                        result += [{"url": GITHUB_URL + soupFound[i].get('href')}]
                    else:
                        raise self.DataNotFoundException
        else:
            if not (soup.find("div", {"class": CLASS_TO_SEARCH['CheckIfThereIsResultIssue']})
                    if self.type == 'Issues'
                    else soup.find("div", {"class": CLASS_TO_SEARCH['CheckIfThereIsResultRepositoryAndWiki']})):
                return [{"url_not_found": "Not found any URL for this search."}]
            else:
                raise self.DataNotFoundException

        return result

    def generateURL(self):
        """ This function generate a valid URL to downloaded.

        Output: Valid URL (String).
        """

        if len(self.keywords) > 1:
            return GITHUB_SEARCH_URL + "".join([str(_) + '+' for _ in self.keywords])[:-1] + '&type=' + self.type
        else:
            return GITHUB_SEARCH_URL + str(self.keywords[0]) + '&type=' + self.type

    def run(self):
        """ Run function of the crawler. GitHub crawler that implements the GitHub search and returns all the links
            from the search result.

        Output: List of URL of the search.
        """

        attempts = self.totalAttempts
        urlToSearch = self.generateURL()

        if self.print_info:
            print("SEARCHING: " + str(urlToSearch))

        while True:
            try:
                urls = self.getURLs(self.downloadHTML(urlToSearch))
                if self.print_info:
                    print("Result after " + str(self.totalAttempts - attempts) + " attempts.")
                return urls
            except requests.exceptions.RequestException:
                if self.print_info:
                    print("ERROR: " + str(sys.exc_info()[1]))
                attempts -= 1
                if attempts == 0:
                    if self.print_info:
                        print("FAIL after " + str(self.totalAttempts) + " attempts.")
                    return [{
                        'error': str(sys.exc_info()[1])
                    }]
            except self.DataNotFoundException as e:
                if self.print_info:
                    print("ERROR: " + str(e))
                    print("FAIL after " + str(self.totalAttempts - attempts) + " attempts.")
                return [{
                    'error': str(e)
                }]
