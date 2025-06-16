import unittest
from app import main


class TestDnsRecords(unittest.TestCase):

    def test_parse_subdomains_empty(self):
        subdomains = ""
        default_rrtype = "A"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("@", "A")])
        default_rrtype = "AAAA"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("@", "AAAA")])

    def test_parse_subdomains_no_rrtype(self):
        subdomains = "test"
        default_rrtype = "A"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("test", "A")])
        default_rrtype = "AAAA"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("test", "AAAA")])

    def test_parse_subdomains_with_rrtype(self):
        subdomains = "test{AAAA}"
        default_rrtype = "A"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("test", "AAAA")])
        subdomains = "test{A}"
        default_rrtype = "AAAA"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("test", "A")])

    def test_parse_subdomains_multiple(self):
        subdomains = "testa{AAAA},testb{A},testc{AAAA},testd"
        default_rrtype = "A"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("testa", "AAAA"), ("testb", "A"), ("testc", "AAAA"), ("testd", "A")])
        default_rrtype = "AAAA"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("testa", "AAAA"), ("testb", "A"), ("testc", "AAAA"), ("testd", "AAAA")])

    def test_parse_subdomains_trailing_comma(self):
        subdomains = "test,"
        default_rrtype = "A"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("test", "A")])

    def test_parse_subdomains_double_comma(self):
        subdomains = "testa,,testb"
        default_rrtype = "A"
        self.assertEqual(main.parse_subdomains(subdomains, default_rrtype), [("testa", "A"), ("testb", "A")])

if __name__ == '__main__':
    unittest.main()