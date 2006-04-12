from StringIO import StringIO
import csv
import re

from zope import interface
from zope import component
from path import path

import CipraSync.interfaces
import CipraSync.read
import CipraSync.utils

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


class MemberReader(CipraSync.read.Reader):
    """A reader that extends ``CipraSync.read.Field`` and adds its own
    field factory.

    >>> from path import path
    >>> from minaraad.sync import configure

    >>> configure.transforms()

    >>> parent = path(__file__).parent
    >>> configuration = parent / 'etc' / 'memberreader.ini'
    >>> reader = MemberReader(configuration=configuration)
    >>> reader # doctest: +ELLIPSIS
    <minaraad.sync.read.MemberReader instance ...>

    >>> reader.feed((parent / 'input' / 'Nieuwbriefbestand.csv',))
    >>> records = list(reader)
    >>> dontcare = [r._doTransforms() for r in records]
    >>> len(records)
    2685
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


class StupidTransformReader:
    """A reader that takes a list of names and looks up one transform
    per name.

    >>> from path import path
    >>> from minaraad.sync import configure

    >>> configure.transforms()

    >>> parent = path(__file__).parent
    >>> configuration = parent / 'etc' / 'stupidreader.ini'
    >>> reader = StupidTransformReader(configuration=configuration)
    >>> reader # doctest: +ELLIPSIS
    <minaraad.sync.read.StupidTransformReader instance ...>
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(CipraSync.interfaces.IReader, reader)
    True

    >>> len (reader._transform_map)
    3

    Now we define our own transform to verify that they are called
    correctly:

    >>> from CipraSync.interfaces import ITransform
    >>> class MyTransform:
    ...     interface.implements(ITransform)
    ...     def __init__(self, id):
    ...         self.id = id
    ...     def __call__(self, name):
    ...         return ['%r called with %r' % (self.id, name)]

    >>> for name in ('adviezen', 'newsletter', 'pressrelease'):
    ...     component.provideUtility(
    ...         MyTransform(name),
    ...         name='mina-transform-%sscrape' % name,
    ...     )

    Now call feed and then iterate over the records:

    >>> reader.feed(('blatabladbla', 'nieuwsbrieffoo', 'hihipersberichten'))
    >>> tuple(reader)
    ("'adviezen' called with 'blatabladbla'", "'newsletter' called with 'nieuwsbrieffoo'", "'pressrelease' called with 'hihipersberichten'")

    Now feed some foobar and see how it fails:

    >>> reader.feed(('foobar',))
    >>> tuple(reader) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Found no transform for 'foobar'.
    """
    interface.implements(CipraSync.interfaces.IReader)
    
    def __init__(self, configuration=None):
        """Initialize with a given configuration filename."""
        if configuration is None:
            configuration = path(__file__).parent / 'etc' / 'stupidreader.ini'
        
        self._processConfiguration(configuration)

    def feed(self, data):
        """Expects data to be a list of names.  These can be
        filenames, URIs or anything.

        See IReader.
        """
        self._names = data
        
    def __iter__(self):
        """See IReader."""

        def iterRecords():
            for name in self._names:
                match = False
                for expr, tname in self._transform_map.items():
                    if re.match(expr, name):
                        match = True
                        self.logger.debug("Using %r transform for %r." %
                                          (tname, name))
                        tform = component.getUtility(
                            CipraSync.interfaces.ITransform, name=tname)
                        for record in tform(name):
                            yield record

                if not match:
                    msg = "Found no transform for %r." % name
                    self.logger.critical(msg)
                    raise ValueError(msg)

            raise StopIteration

        return iterRecords()

    def _processConfiguration(self, configuration):
        """Process configuration from filename."""
        self.cfg = CipraSync.utils.readConfiguration(configuration)
        self.logger = CipraSync.utils.getLogger(self.cfg.get('Logging.name'))

        try:
            self._transform_map = eval(self.cfg.get('Transforms.map'))
        except TypeError, e:
            self.logger.critial("Could not read 'Transforms.map' "
                                "configuration variable.")
            raise

