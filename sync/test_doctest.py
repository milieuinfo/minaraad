import unittest
from doctest import DocTestSuite

import utils

MODULENAMES = (
    'minaraad.sync.read',
    'minaraad.sync.write',
    'minaraad.sync.transform',
    )

def test_suite():
    suites = []
    for module in MODULENAMES:
        utils.setUpEnviron()
        suites.append(DocTestSuite(module))
        utils.tearDownEnviron()

    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
