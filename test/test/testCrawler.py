import requests
import unittest
from unittest import TestCase, mock
from githubCrawler.src.githubCrawler.githubCrawler import GithubCrawler


class TestCrawler(TestCase):
    """  Tests for GitHub crawler """

    def testInvalidKeyword(self):
        """Test that checks KeyWordNotValid Exception is raised if Keywords not valid."""

        try:
            GithubCrawler('../json/invalidKeywords.json').run()
        except GithubCrawler.KeyWordNotValid:
            pass
        except Exception:
            self.fail('unexpected exception raised')
        else:
            self.fail('unexpected exception raised')

    def testInvalidType(self):
        """Test that checks TypeNotValid Exception is raised if Type not valid."""

        try:
            GithubCrawler('../json/invalidType.json').run()
        except GithubCrawler.TypeNotValid:
            pass
        except Exception:
            self.fail('unexpected exception raised')
        else:
            self.fail('unexpected exception raised')

    def testInvalidProxies(self):
        """Test that checks ProxyNotValid Exception is raised if Proxies not valid."""

        try:
            GithubCrawler('../json/invalidProxies.json').run()
        except GithubCrawler.ProxyNotValid:
            pass
        except Exception:
            self.fail('unexpected exception raised')
        else:
            self.fail('unexpected exception raised')

    @mock.patch("requests.get")
    def testNoConnection(self, mock_get):
        """Test that checks if requests.exceptions.RequestException Exception is raised if bad connection """

        mock_get.side_effect = requests.exceptions.RequestException

        try:
            response = GithubCrawler('../json/python_java_issues.json').run()
            self.assertEqual(response, [{'error': ""}])

        except requests.exceptions.RequestException:
            self.fail('unexpected exception raised')
        except Exception:
            self.fail('unexpected exception raised')

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testRepositories(self, mock_get):
        """Test that crawler of repositories' URL works correctly """

        with open('../html/python_java_repositories.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_repositories.json').run()

        expectedResponse = [{'url': 'https://github.com/qiyuangong/leetcode',
                             'extra': {'owner': 'qiyuangong', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/itwanger/JavaBooks',
                             'extra': {'owner': 'itwanger', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/natural/java2python',
                             'extra': {'owner': 'natural', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/kivy/pyjnius',
                             'extra': {'owner': 'kivy', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/yusugomori/DeepLearning',
                             'extra': {'owner': 'yusugomori', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/ninia/jep',
                             'extra': {'owner': 'ninia', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/OGRECave/ogre',
                            'extra': {'owner': 'OGRECave', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/c2nes/javalang',
                            'extra': {'owner': 'c2nes', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/bytedeco/javacpp-presets',
                            'extra': {'owner': 'bytedeco', 'language_stats': 'Not data about languages'}},
                            {'url': 'https://github.com/RyanFehr/HackerRank',
                            'extra': {'owner': 'RyanFehr', 'language_stats': 'Not data about languages'}}]

        self.assertEqual(all(url in response for url in expectedResponse), True)

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testRepositoriesBadURL(self, mock_get):
        """Test that crawler of repositories' URL works correctly when HTML text is not correct or has changed """

        with open('../html/python_java_repositories_bad.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_repositories.json').run()

        self.assertEqual(response, [{'error': 'Data not found. Github HTML may have changed.'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testRepositoriesNoURLFound(self, mock_get):
        """Test that crawler of repositories' URL works correctly when no URL is found"""

        with open('../html/no_repositories.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_repositories.json').run()

        self.assertEqual(response, [{'url_not_found': 'Not found any URL for this search.'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testExtraCorrect(self, mock_get):
        """Test that crawler of extra info of a repository works correctly. All the info is available """

        with open('../html/extra_case_correct.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_repositories.json').getRepositoryInfoWithExtra('/qiyuangong/leetcode')

        self.assertEqual(response, [{'url': 'https://github.com/qiyuangong/leetcode',
                                     'extra': {'owner': 'qiyuangong',
                                               'language_stats': {'Python': '77.4', 'Java': '20.4', 'C++': '2.2'}}}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testExtraIncorrect(self, mock_get):
        """Test that crawler of extra info of a repository works correctly.
        In this test there is not language stats info available"""

        with open('../html/extra_case_incorrect.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_repositories.json').getRepositoryInfoWithExtra('/itwanger/JavaBooks')

        self.assertEqual(response, [{'url': 'https://github.com/itwanger/JavaBooks',
                                     'extra': {'owner': 'itwanger', 'language_stats': 'Not data about languages'}}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testExtraNoConnection(self, mock_get):
        """Test that crawler of extra info of a repository works correctly.
        In this test there is no connection"""

        mock_get.side_effect = requests.exceptions.RequestException

        response = GithubCrawler('../json/python_java_repositories.json').getRepositoryInfoWithExtra('/qiyuangong/leetcode')

        self.assertEqual(response, [{'extra': {'language_stats': {'error': ''}, 'owner': 'qiyuangong'},
                                     'url': 'https://github.com/qiyuangong/leetcode'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testIssues(self, mock_get):
        """Test that crawler of issues' URL works correctly """

        with open('../html/python_java_issues.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_issues.json').run()

        self.assertEqual(response, [{'url': 'https://github.com/debrajhyper/Topic_Learning_Resources/issues'},
                                    {'url': 'https://github.com/girlscript/winter-of-contributing/issues'},
                                    {'url': 'https://github.com/girlscript/winter-of-contributing/issues'},
                                    {'url': 'https://github.com/girlscript/winter-of-contributing/issues'},
                                    {'url': 'https://github.com/coolkiranmehta/hacktoberfest-hacktoberfest-21/issues'},
                                    {'url': 'https://github.com/keshavsingh4522/hacktoberfest2021/issues'},
                                    {'url': 'https://github.com/amisha-28/Hacktoberfest2021/issues'},
                                    {'url': 'https://github.com/girlscript/winter-of-contributing/issues'},
                                    {'url': 'https://github.com/girlscript/winter-of-contributing/issues'},
                                    {'url': 'https://github.com/girlscript/winter-of-contributing/issues'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testIssuesBadURL(self, mock_get):
        """Test that crawler of issues' URL works correctly when HTML text is not correct or has changed"""

        with open('../html/python_java_issues_bad.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_issues.json').run()

        self.assertEqual(response, [{'error': 'Data not found. Github HTML may have changed.'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testIssuesNoURLFound(self, mock_get):
        """Test that crawler of issues' URL works correctly when no URL is found"""

        with open('../html/no_issues.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_issues.json').run()

        self.assertEqual(response, [{'url_not_found': 'Not found any URL for this search.'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testWikis(self, mock_get):
        """Test that crawler of wikis' URL works correctly """

        with open('../html/python_java_wikis.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_wikis.json').run()

        self.assertEqual(response, [{'url': 'https://github.com/blfranciscovich/comp830gradproject'},
                                    {'url': 'https://github.com/masmangan/bugfree-lana'},
                                    {'url': 'https://github.com/CS2613-FA2021/journal-entries-BrendanD7'},
                                    {'url': 'https://github.com/Ignat99/msp'},
                                    {'url': 'https://github.com/wekan/wekan'},
                                    {'url': 'https://github.com/dchassin/gridlabd-slac'},
                                    {'url': 'https://github.com/CS2613-FA2021/journal-entries-graceashfield'},
                                    {'url': 'https://github.com/jeenuine/eye-messenger'},
                                    {'url': 'https://github.com/cloudron-io/wekan'},
                                    {'url': 'https://github.com/oeli/yafra'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testWikisBadURL(self, mock_get):
        """Test that crawler of wikis' URL works correctly when HTML text is not correct or has changed"""

        with open('../html/python_java_wikis_bad.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_wikis.json').run()

        self.assertEqual(response, [{'error': 'Data not found. Github HTML may have changed.'}])

    @mock.patch.object(GithubCrawler, "downloadHTML")
    def testWikisNoURLFound(self, mock_get):
        """Test that crawler of wikis' URL works correctly when no URL is found"""

        with open('../html/no_wikis.txt', encoding="utf8") as file:
            expectedHTML = file.read()

        mock_get.return_value = expectedHTML

        response = GithubCrawler('../json/python_java_wikis.json').run()

        self.assertEqual(response, [{'url_not_found': 'Not found any URL for this search.'}])

    def testGenerateURLMoreThanOneKeyword(self):
        """Test GenerateURL function. Test if there is more than one keyword"""

        response = GithubCrawler('../json/python_java_jira_repositories.json').generateURL()

        self.assertEqual(response, 'https://github.com/search?q=Python+Java+Jira&type=Repositories')

    def testGenerateURLJustOneKeyword(self):
        """Test GenerateURL function. Test if there is just one keyword"""

        response = GithubCrawler('../json/python_repositories.json').generateURL()

        self.assertEqual(response, 'https://github.com/search?q=Python&type=Repositories')


if __name__ == '__main__':
    unittest.main()
