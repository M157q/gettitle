import unittest

from unittest.mock import Mock

from gettitle import gettitle, exceptions


class TestCheckAndReconstructUrl(unittest.TestCase):

    def setUp(self):
        self.http_url = "http://google.com"
        self.https_url = "https://google.com"

    def test_correct_url(self):
        ''' Should return same url if the input url is correct. '''

        self.assertEqual(
            self.http_url,
            gettitle.check_and_reconstruct_url(self.http_url)
        )
        self.assertEqual(
            self.https_url,
            gettitle.check_and_reconstruct_url(self.https_url)
        )

    def test_empty_url(self):
        ''' Should raise EmptyUrlError.  '''

        self.assertRaises(exceptions.EmptyUrlError,
                          gettitle.check_and_reconstruct_url, '')

    def test_url_with_leading_space(self):
        ''' Should remove leading space.  '''

        self.assertEqual(
            self.http_url,
            gettitle.check_and_reconstruct_url(" http://google.com")
        )
        self.assertEqual(
            self.https_url,
            gettitle.check_and_reconstruct_url(" https://google.com")
        )

    def test_url_with_leading_spaces(self):
        ''' Should remove leading spaces.  '''

        self.assertEqual(
            self.http_url,
            gettitle.check_and_reconstruct_url("    http://google.com")
        )
        self.assertEqual(
            self.https_url,
            gettitle.check_and_reconstruct_url("    https://google.com")
        )

    def test_url_with_trailing_space(self):
        ''' Should remove trailing space.  '''

        self.assertEqual(
            self.http_url,
            gettitle.check_and_reconstruct_url("http://google.com ")
        )
        self.assertEqual(
            self.https_url,
            gettitle.check_and_reconstruct_url("https://google.com ")
        )

    def test_url_with_trailing_spaces(self):
        ''' Should remove trailing spaces.  '''

        self.assertEqual(
            self.http_url,
            gettitle.check_and_reconstruct_url("http://google.com   ")
        )
        self.assertEqual(
            self.https_url,
            gettitle.check_and_reconstruct_url("https://google.com   ")
        )

    def test_broken_scheme_url(self):
        ''' Should replace scheme which is not http or https to http '''

        self.assertEqual(
            self.http_url,
            gettitle.check_and_reconstruct_url("ttp://google.com")
        )


class TestGetTitlesAndUrls(unittest.TestCase):

    def setUp(self):
        self.args = Mock(urls=None, markdown=False, rst=False, debug=False)
        self.br = gettitle.set_browser()

    def tearDown(self):
        del self.args
        gettitle.unset_browser(self.br)

    def test_google(self):
        self.args.urls = ["http://google.com"]
        s = gettitle.get_titles_and_urls(self.br, self.args)[0][:-1]
        title, url = s.split('\n')

        self.assertEqual("Google", title)
        self.assertTrue("https://www.google.com" in url)

    def test_ptt_normal(self):
        self.args.urls = [
            "https://www.ptt.cc/bbs/joke/M.1442444784.A.1C4.html"
        ]
        s = gettitle.get_titles_and_urls(self.br, self.args)[0][:-1]
        title, url = s.split('\n')

        self.assertEqual(
            "[豪洨] 成語新解--弘庭戴套 - 看板 joke - 批踢踢實業坊",
            title
        )
        self.assertEqual(
            "https://www.ptt.cc/bbs/joke/M.1442444784.A.1C4.html",
            url
        )

    def test_ptt_ask_over_18(self):
        ''' Need to submit "yes" to the action="/ask/over18/" form '''

        self.args.urls = [
            "https://www.ptt.cc/bbs/Gossiping/M.1441715120.A.72E.html"
        ]
        s = gettitle.get_titles_and_urls(self.br, self.args)[0][:-1]
        title, url = s.split('\n')

        self.assertEqual(
            "Re: [爆卦] 9/19 台灣失智症協會 一日志工 - 看板 Gossiping - 批踢踢實業坊",
            title
        )
        self.assertEqual(
            "https://www.ptt.cc/bbs/Gossiping/M.1441715120.A.72E.html",
            url
        )

    def test_hackpad(self):
        ''' Hackpad title is returned in unicode format. '''

        self.args.urls = [
            "https://hackpad.com/iToolMan-T-cOJlcwLntzx"
        ]
        s = gettitle.get_titles_and_urls(self.br, self.args)[0][:-1]
        title, url = s.split('\n')

        self.assertEqual(
            "iToolMan 工具人帽T討論 - hackpad.com",
            title
        )
        self.assertEqual(
            "https://hackpad.com/iToolMan-T-cOJlcwLntzx",
            url
        )

    def test_ruten(self):
        ''' Ruten title is returned in big5 format. '''

        self.args.urls = [
            "http://www.ruten.com.tw/"
        ]
        s = gettitle.get_titles_and_urls(self.br, self.args)[0][:-1]
        title, url = s.split('\n')

        self.assertEqual(
            "露天拍賣-台灣 NO.1 拍賣網站",
            title
        )
        self.assertEqual(
            "http://www.ruten.com.tw/",
            url
        )

    def test_dcard(self):
        ''' grab dcard title with dryscrape which supports javascript. '''

        self.args.urls = [
            "https://www.dcard.tw/f/bg/p/706907"
        ]
        s = gettitle.get_titles_and_urls(self.br, self.args)[0][:-1]
        title, url = s.split('\n')

        self.assertEqual(
            "駕照 附贈閃光一枚 - Dcard",
            title
        )
        self.assertEqual(
            "https://www.dcard.tw/f/bg/p/706907",
            url
        )
