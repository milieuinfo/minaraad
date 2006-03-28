from StringIO import StringIO
import csv

import CipraSync.read

class Field(CipraSync.read.Field):
    """A field that uses the ``csv`` package to consume data from a
    line.

    >>> field = Field('somefield')
    >>> data = '"Abts","Hugo","De heer"'
    >>> value, line = field.eat(data)
    >>> value
    'Abts'
    >>> line.strip()
    'Hugo,De heer'
    >>> value, line = field.eat(line)
    >>> value
    'Hugo'
    >>> line.strip()
    'De heer'

    Let's try out the consume argument to see if it works for our
    subclass:

    >>> field = Field(name='somefield', consume=2)
    >>> value, line = field.eat(data)
    >>> value
    ['Abts', 'Hugo']
    >>> line.strip()
    'De heer'

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
    >>> line.strip()
    'Hugo,De heer'
    """

    dialect = 'excel'

    def eat(self, line):
        reader = csv.reader([line], dialect=self.dialect)
        [row] = list(reader)

        data = row[:self.consume]
        line = row[self.consume:]

        if len(data) == 1:
            data = data[0]

        out = StringIO()
        writer = csv.writer(out, dialect=self.dialect)
        writer.writerows([line])

        for transform in self.transforms:
            data = transform(data)

        return data, out.getvalue()


class Reader(CipraSync.read.Reader):
    """A reader that extends ``CipraSync.read.Field`` and adds its own
    field factory.

    
    """
    
    def fieldFactory(self, *args, **kwargs):
        return Field(*args, **kwargs)
