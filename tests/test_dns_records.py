import unittest
from app import dns_records


class TestDnsRecords(unittest.TestCase):


    def test_from_json(self):
        json = '''[
            {"id": 0,"hostname": "@","type": "A","target": "123.123.123.123"},
            {"id": 1,"hostname": "www","type": "A","target": "123.456.789.10"},
            {"id": 2,"hostname": "mail","type": "A","target": "123.123.234.234"},
            {"id": 3,"hostname": "@","type": "MX","target": "mail.example.de","prio": "10"},
            {"id": 4,"hostname": "example.de","type": "TXT","target": "text"},
            {"id": 5,"hostname": "abc","type": "A","target": "78.78.78.80"}]'''

        records = dns_records.from_json(json)
        self.assertIsNotNone(records)
        self.assertIs(type(records), list)

        self.assertEqual(len(records),6)
        self.assertIs(type(records[0]), dict)
        self.assertDictEqual(records[0], {"id": 0,"hostname": "@","type": "A","target": "123.123.123.123"})
        self.assertIs(type(records[1]), dict)
        self.assertDictEqual(records[1], {"id": 1,"hostname": "www","type": "A","target": "123.456.789.10"})
        self.assertIs(type(records[2]), dict)
        self.assertDictEqual(records[2], {"id": 2,"hostname": "mail","type": "A","target": "123.123.234.234"})
        self.assertIs(type(records[3]), dict)
        self.assertDictEqual(records[3], {"id": 3,"hostname": "@","type": "MX","target": "mail.example.de","prio": "10"})
        self.assertIs(type(records[4]), dict)
        self.assertDictEqual(records[4], {"id": 4,"hostname": "example.de","type": "TXT","target": "text"})
        self.assertIs(type(records[5]), dict)
        self.assertDictEqual(records[5], {"id": 5,"hostname": "abc","type": "A","target": "78.78.78.80"})

 
    def test_to_form_url_encoded(self):
        records = [
            {"id": 0,"hostname": "@","type": "A","target": "123.123.123.123"},
            {"id": 1,"hostname": "www","type": "A","target": "123.456.789.10"},
            {"id": 2,"hostname": "mail","type": "A","target": "123.123.234.234"},
            {"id": 3,"hostname": "@","type": "MX","target": "mail.example.de","prio": "10"},
            {"id": 4,"hostname": "example.de","type": "TXT","target": "text"},
            {"id": 5,"hostname": "abc","type": "A","target": "78.78.78.80"}]

        url_encoded = dns_records.to_form_url_encoded(records)
        print(url_encoded)
        self.assertEquals(url_encoded, (
            'records[0][id]=0&records[0][hostname]=@&records[0][type]=A&records[0][target]=123.123.123.123&'
            'records[1][id]=1&records[1][hostname]=www&records[1][type]=A&records[1][target]=123.456.789.10&'
            'records[2][id]=2&records[2][hostname]=mail&records[2][type]=A&records[2][target]=123.123.234.234&'
            'records[3][id]=3&records[3][hostname]=@&records[3][type]=MX&records[3][target]=mail.example.de&records[3][prio]=10&'
            'records[4][id]=4&records[4][hostname]=example.de&records[4][type]=TXT&records[4][target]=text&'
            'records[5][id]=5&records[5][hostname]=abc&records[5][type]=A&records[5][target]=78.78.78.80'))

if __name__ == '__main__':
    unittest.main()