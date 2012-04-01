#!/usr/bin/env python2.7
# vim: fileencoding=utf-8
from __future__ import unicode_literals
import unittest
import cStringIO
import csvwrapper
import itertools

class TestWriter(unittest.TestCase):

    def test_StringIO(self):
        inputs = [
                ["a", "", 123],
                ["あいうえお", "abc", ""],
                ["abc,def\",,,"]
                ]
        expect = (
                "a,,123\r\n"
                "あいうえお,abc,\r\n"
                "\"abc,def\"\",,,\"\r\n"
                ).encode('cp932')
        f = cStringIO.StringIO()

        with csvwrapper.writer(f, encoding='cp932') as writer:
            writer.writerows(inputs)
            self.assertEquals(f.getvalue(), expect)
        self.assertEquals(f.closed, True)

class TestDictWriter(unittest.TestCase):

    def test_StringIO(self):
        fieldnames = ["Field1", "Field2"]
        inputs = [
                {"Field1": "a", "Field2": "", "Field3": 123},
                {"Field1": "あいうえお", "Field2": "abc", "Field3": ""},
                {"Field1": "abc,def\",,,"}
                ]
        expect = (
                "Field1,Field2\r\n"
                "a,\r\n"
                "あいうえお,abc\r\n"
                "\"abc,def\"\",,,\",\r\n"
                ).encode('cp932')
        f = cStringIO.StringIO()

        with csvwrapper.DictWriter(f, encoding='cp932', fieldnames=fieldnames, extrasaction='ignore') as writer:
            writer.writeheader()
            writer.writerows(inputs)
            self.assertEquals(f.getvalue(), expect)
        self.assertEquals(f.closed, True)

if __name__ == '__main__':
    unittest.main()

