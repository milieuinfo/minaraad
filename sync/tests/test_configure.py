import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctest import ELLIPSIS

from zope import component

from CipraSync import interfaces


import utils

def setUp(test):
    utils.setUpEnviron()

def tearDown(test):
    utils.tearDownEnviron()

class TestConfigure:


    def test_resolver(self):
        """
        >>> from minaraad.sync import configure
        >>> configure.resolver()
        >>> #component.getUtility(interfaces.IPathResolver, 'mina-resolver')
        """

    def test_transforms(self):
        """
        >>> from minaraad.sync import configure
        >>> configure.transforms()
        >>> names = ('dontwrite', 'streetandhousenumber', 'zipcodeandcity',
        ...          'street', 'housenumber', 'bus', 'zipcode', 'city',
        ...          'country')
        >>> names = ['mina-transform-%s' % name for name in names]
        >>> for name in names:
        ...     t = component.getUtility(interfaces.ITransform, name)
        """

    def test_reader(self):
        """
        >>> from minaraad.sync import configure
        >>> configure.transforms() # required for the reader to work
        >>> configure.reader()
        >>> component.getUtility(interfaces.IReader)
        <minaraad.sync.read.Reader instance ...>
        """

    def test_writer(self):
        """
        >>> from minaraad.sync import configure
        >>> configure.transforms() # required for the reader to work
        >>> configure.reader()
        >>> configure.writer()
        >>> reader = component.getUtility(interfaces.IReader)
        >>> interfaces.IWriter(reader)
        <CipraSync.write.Writer instance ...>
        """


def test_suite():
    return DocTestSuite(setUp=setUp, tearDown=tearDown, optionflags=ELLIPSIS)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
