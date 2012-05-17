#!/usr/bin/env python2.7
# vim: fileencoding=utf-8
from __future__ import unicode_literals
import csv
import codecs
import numbers
from itertools import chain, repeat, izip
from csv import (register_dialect, unregister_dialect, get_dialect,
                 list_dialects, field_size_limit, Dialect, excel, excel_tab,
                 Sniffer, QUOTE_ALL, QUOTE_MINIMAL, QUOTE_NONNUMERIC,
                 QUOTE_NONE, Error)

class IterableRecoder(object):

    def __init__(self, iterable, decoder, encoder, errors='strict'):
        self._iter = iter(iterable)
        self._decoder = decoder
        self._encoder = encoder
        self._errors = errors

    def __iter__(self):
        return self

    def next(self):
        line = self._iter.next()
        return self._encoder(self._decoder(line, self._errors)[0],
                             self._errors)[0]

def reader(csvfile, encoding, errors='strict', dialect='excel', **kwds):
    utf_8_encoder = codecs.getencoder('utf_8')
    if hasattr(csvfile, 'read'):
        recoder = codecs.StreamRecoder(csvfile,
                                       utf_8_encoder,
                                       codecs.getdecoder('undefined'),
                                       codecs.getreader(encoding),
                                       codecs.getwriter('undefined'),
                                       errors)
    else:
        recoder = IterableRecoder(csvfile,
                                  codecs.getdecoder(encoding),
                                  utf_8_encoder,
                                  errors)

    if hasattr(csvfile, 'close'):
        stream = csvfile
    else:
        stream = None

    reader = csv.reader(recoder, dialect=dialect, **kwds)
    return csvreader(stream, reader, codecs.getdecoder('utf_8'), errors)

def writer(csvfile, encoding, errors='strict', dialect='excel', **kwds):
    recoder = codecs.StreamRecoder(csvfile,
                                   codecs.getencoder('undefined'),
                                   codecs.getdecoder('utf_8'),
                                   codecs.getreader('undefined'),
                                   codecs.getwriter(encoding),
                                   errors)
    if hasattr(csvfile, 'close'):
        stream = csvfile
    else:
        stream = None

    writer = csv.writer(recoder, dialect=dialect, **kwds)
    return csvwriter(stream, writer, codecs.getencoder('utf_8'), errors)

class csvreader(object):
    def __init__(self, stream, reader, decoder, errors):
        self._stream = stream
        self._reader = reader
        self._decoder = decoder
        self._errors = errors

    def __iter__(self):
        return self

    def next(self):
        if self._reader is None:
            raise Error("File is already closed.")
        return [self._decoder(cell, self._errors)[0]
                for cell in self._reader.next()]

    @property
    def dialect(self):
        if self._reader is None:
            raise Error("File is already closed.")
        return self._reader.dialect

    @property
    def line_num(self):
        if self._reader is None:
            raise Error("File is already closed.")
        return self._reader.line_num

    ############# Additions #############

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def close(self):
        self._reader = None
        if self._stream:
            self._stream.close()
            self._stream = None

class csvwriter(object):
    def __init__(self, stream, writer, encoder, errors):
        self._stream = stream
        self._writer = writer
        self._encoder = encoder
        self._errors = errors

    def writerow(self, row):
        def convert(cell):
            if isinstance(cell, numbers.Number):
                cell = unicode(cell)
            return self._encoder(cell, self._errors)[0]

        self._writer.writerow(map(convert, row))

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    @property
    def dialect(self):
        if self._writer is None:
            raise Error("File is already closed.")
        return self._writer.dialect

    ############# Additions #############

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def close(self):
        self._writer = None
        if self._stream:
            self._stream.close()
            self._stream = None

class DictReader(object):
    def __init__(self, csvfile, encoding, errors='strict', fieldnames=None,
                 restkey=None, restval=None, dialect='excel', *args, **kwds):
        self._reader = reader(csvfile, encoding, errors, dialect, *args, **kwds)
        self._fieldnames = fieldnames
        self._restkey = restkey
        self._restval = restval

    def __iter__(self):
        return self

    def _get_row(self):
        row = []
        # For compatibility, we skip the empty rows.
        # See the original csv.py in Python2.7.
        while row == []:
            row = self._reader.next()
        return row

    def next(self):
        if self._reader is None:
            raise Error("File is already closed.")

        if self._fieldnames is None:
            self._fieldnames = self._get_row()

        row = self._get_row()
        ret = dict()
        for key, value in izip(self._fieldnames,
                               chain(row, repeat(self._restval))):
            ret[key] = value
        if len(self._fieldnames) < len(row):
            ret[self._restkey] = row[len(self._fieldnames):]
        return ret

    @property
    def dialect(self):
        if self._reader is None:
            raise Error("File is already closed.")
        return self._reader.dialect

    @property
    def line_num(self):
        if self._reader is None:
            raise Error("File is already closed.")
        return self._reader.line_num

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            self._fieldnames = self._get_row()

        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    ############# Additions #############

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def close(self):
        if self._reader:
            self._reader.close()
            self._reader = None

class DictWriter(object):
    def __init__(self, csvfile, encoding, fieldnames, errors='strict',
                 restval='', extrasaction='raise', dialect='excel', *args,
                 **kwds):
        self._writer = writer(csvfile, encoding, errors, dialect, *args, **kwds)
        self._fieldnames = fieldnames
        self._restval = restval
        self._extrasaction = extrasaction

    def writerow(self, rowdict):
        if self._writer is None:
            raise Error("File is already closed.")

        if self._extrasaction == 'raise':
            for key in rowdict.iterkeys():
                if key not in self._fieldnames:
                    raise ValueError('dict contains fields not in fieldnames:'
                                     ' %s' % key)
        self._writer.writerow([rowdict.get(key, self._restval)
                               for key in self._fieldnames])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def writeheader(self):
        self._writer.writerow(self._fieldnames)

    @property
    def dialect(self):
        if self._writer is None:
            raise Error("File is already closed.")
        return self._writer.dialect

    @property
    def fieldnames(self):
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    ############# Additions #############

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def close(self):
        if self._writer:
            self._writer.close()
            self._writer = None

