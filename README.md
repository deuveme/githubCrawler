# Github Crawler
GitHub crawler that implements the GitHub search and returns all the links from the search result.

## Requires ##
To execute this package you need to have correctly downloaded:
- Python >= 3.
- The following libraries:
    - JSON, https://docs.python.org/3/library/json.html
    - Sys, https://docs.python.org/3/library/sys.html
    - Random, https://docs.python.org/3/library/random.html
    - Requests, https://docs.python-requests.org/. To download: `pip install requests`
    - BeautifulSoup, https://www.crummy.com/software/BeautifulSoup/bs4/doc/. To download: `pip install beautifulsoup4`

## Files and their functionality ##
### Folder ./src/githubCrawler ###
All the source code of the project.

- **githubCrawler.py**
  Script with all the library of the crawler and their functions, to run the library you just need to:
  - Import the library on your own script.
  - Execute:
  
  `GithubCrawler(link, number_attempts).run()`
  
  Where:
  - `link` Is a link to a JSON with the following data:
    - Keywords: A list of keywords to be used as search terms.
    - Proxies: One of them should be selected and used randomly to perform all the HTTP requests.
    - Type: The type of object we are searching for (Repositories, Issues or Wikis)
      
    Here you have and example:
    `{
        "keywords": ["Python", "Java"],
        "proxies": ["71.237.233.224:8118","136.228.141.154:80"],
        "type": "Issues"
    }`
  - `number_attempts` is the number of attempts the project will do if the connection fails, if value is not set, 
    the default value will be assigned, 20.
  - `print_info` is a bool, if True the process will print some info about it, if False no info will be printed until 
    the process is finished. If value is not set, the default value will be assigned, False.
  
  Once run, the crawler will generate a JSON with all the URLs results.

### Folder ./test/ ###
All the unit test to test the project. If you want to execute all the test: `python test_crawler.py`