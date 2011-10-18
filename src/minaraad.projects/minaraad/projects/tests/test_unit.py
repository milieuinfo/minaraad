import unittest

from zope.testing import doctest

from Products.PloneTestCase import PloneTestCase as ptc
ptc.setupPloneSite()

import base


def test_suite():
    return unittest.TestSuite([
        doctest.DocTestSuite(module='minaraad.projects.validators',
                             optionflags=base.OPTIONFLAGS),
        doctest.DocTestSuite(module='minaraad.projects.utils',
                             optionflags=base.OPTIONFLAGS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
