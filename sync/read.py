from StringIO import StringIO
import csv

import CipraSync.read

class Field(CipraSync.read.Field):
    """A field that uses the ``csv`` package to consume data from a
    line.

    >>> field = Field('somefield')
    >>> data = ['Abts', 'Hugo', 'De heer']
    >>> value, line = field.eat(data)
    >>> value
    'Abts'
    >>> line
    ['Hugo', 'De heer']
    >>> value, line = field.eat(line)
    >>> value
    'Hugo'
    >>> line
    ['De heer']

    Let's try out the consume argument to see if it works for our
    subclass:

    >>> field = Field(name='somefield', consume=2)
    >>> value, line = field.eat(data)
    >>> value
    ['Abts', 'Hugo']
    >>> line
    ['De heer']

    Now we want to try out transforms.  For that, we first create our
    own transform:

    >>> def MyLowerTransform(data):
    ...     return data.lower()

    >>> from zope.interface import directlyProvides
    >>> from CipraSync.interfaces import ITransform
    >>> directlyProvides(MyLowerTransform, ITransform)

    >>> field = Field(name='somefield', transforms=[MyLowerTransform])
    >>> value, line = field.eat(data)
    >>> value
    'abts'
    >>> line
    ['Hugo', 'De heer']
    """

    def eat(self, line):
        data = line[:self.consume]
        line = line[self.consume:]

        if len(data) == 1:
            data = data[0]

        for transform in self.transforms:
            data = transform(data)

        return data, line


class Reader(CipraSync.read.Reader):
    """A reader that extends ``CipraSync.read.Field`` and adds its own
    field factory.

    >>> from path import path
    >>> from minaraad.sync import configure
    >>> from minaraad.sync.read import Reader

    >>> configure.transforms()

    >>> parent = path(__file__).parent
    >>> configuration = parent / 'etc' / 'reader.ini'
    >>> reader = Reader(configuration=configuration)
    >>> reader # doctest: +ELLIPSIS
    <minaraad.sync.read.Reader instance ...>

    >>> reader.feed((parent / 'input' / 'Nieuwbriefbestand.csv',))
    >>> records = list(reader)
    >>> dontcare = [r._doTransforms() for r in records]
    >>> len(records)
    2688
    >>> first = records[0]
    """
    
    dialect = 'excel'

    def fieldFactory(self, *args, **kwargs):
        return Field(*args, **kwargs)

    def _tokenize(self, f):
        reader = csv.reader(f, dialect=self.dialect)        
        for line in reader:
            yield line

        raise StopIteration
