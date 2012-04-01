#!/usr/bin/env python2.7
# vim: fileencoding=utf-8
from __future__ import unicode_literals
import unittest
import cStringIO
import csvwrapper
import itertools

class TestReader(unittest.TestCase):

    def check_equality(self, reader, expects):
        for row, expect_row in itertools.izip_longest(reader, expects):
            self.assertEquals(row, expect_row)

    def test_StringIO(self):
        file_content = (
                "a,,123\r\n"
                "あいうえお,\"abc\",\r\n"
                "\"abc,def\"\",,,\""
                )
        expects = [
                ["a", "", "123"],
                ["あいうえお", "abc", ""],
                ["abc,def\",,,"]
                ]
        f = cStringIO.StringIO(file_content.encode('cp932'))

        with csvwrapper.reader(f, encoding='cp932') as reader:
            self.check_equality(reader, expects)
        self.assertEquals(f.closed, True)

    def test_unicode_array(self):
        input = [
                "a,,123",
                "あいうえお,\"abc\",",
                "\"abc,def\"\",,,\"",
                ]
        expects = [
                ["a", "", "123"],
                ["あいうえお", "abc", ""],
                ["abc,def\",,,"]
                ]
        with csvwrapper.reader(input, encoding='unicode_internal') as reader:
            self.check_equality(reader, expects)

    def test_string_array(self):
        input_unicode = [
                "a,,123",
                "あいうえお,\"abc\",",
                "\"abc,def\"\",,,\"",
                ]
        input = [line.encode('cp932') for line in input_unicode]
        expects = [
                ["a", "", "123"],
                ["あいうえお", "abc", ""],
                ["abc,def\",,,"]
                ]
        with csvwrapper.reader(input, encoding='cp932') as reader:
            self.check_equality(reader, expects)

class TestDictReader(unittest.TestCase):

    def check_equality(self, reader, expects):
        for row, expect_row in itertools.izip_longest(reader, expects):
            self.assertEquals(row, expect_row)

    def test_StringIO(self):
        file_content = (
                "Field1,Field2\r\n"
                "a,123\r\n"
                "あいうえお,\"abc\",\r\n"
                "\"abc,def\"\",,,\""
                )
        expects = [
                {"Field1": "a", "Field2": "123"},
                {"Field1": "あいうえお", "Field2": "abc", "Rest": [""]},
                {"Field1": "abc,def\",,,", "Field2": None}
                ]
        f = cStringIO.StringIO(file_content.encode('cp932'))

        with csvwrapper.DictReader(f, encoding='cp932', restkey='Rest') as reader:
            self.check_equality(reader, expects)
        self.assertEquals(f.closed, True)

    def test_unicode_array(self):
        input = [
                "Field1,Field2",
                "a,123",
                "あいうえお,\"abc\",",
                "\"abc,def\"\",,,\"",
                ]
        expects = [
                {"Field1": "a", "Field2": "123"},
                {"Field1": "あいうえお", "Field2": "abc", "Rest": [""]},
                {"Field1": "abc,def\",,,", "Field2": None}
                ]
        with csvwrapper.DictReader(input, encoding='unicode_internal', restkey='Rest') as reader:
            self.check_equality(reader, expects)

    def test_string_array(self):
        input_unicode = [
                "Field1,Field2",
                "a,123",
                "あいうえお,\"abc\",",
                "\"abc,def\"\",,,\"",
                ]
        input = [line.encode('cp932') for line in input_unicode]
        expects = [
                {"Field1": "a", "Field2": "123"},
                {"Field1": "あいうえお", "Field2": "abc", "Rest": [""]},
                {"Field1": "abc,def\",,,", "Field2": None}
                ]
        with csvwrapper.DictReader(input, encoding='cp932', restkey='Rest') as reader:
            self.check_equality(reader, expects)

if __name__ == '__main__':
    unittest.main()

