try:
    # Theoretically, this product can be used without
    # Products.minaraad (well the interest is quite limited,
    # but it allows us to test all the projects code on Plone4
    # without having to migrate the old code.
    import Products.minaraad
    from Products.minaraad.tests.MainTestCase import MainTestCase
    minaraad_exists = True
    MainTestCase  # pyflakes
except ImportError:
    MainTestCase = object
    minaraad_exists = False

import unittest
from Testing import ZopeTestCase as ztc
from Products.Five import fiveconfigure, zcml

from minaraad.projects.tests.base import OPTIONFLAGS
from minaraad.projects.tests.base import MinaraadFunctionalTestCase


class MinaraadFunctionalMigrationTestCase(
    MinaraadFunctionalTestCase, MainTestCase):
    def install_minaraad(self):
        if not minaraad_exists:
            return

        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml', Products.minaraad)
        fiveconfigure.debug_mode = False
        ztc.installProduct('minaraad')
        self.addProduct('minaraad')

        self._createFolderStructure()


def test_suite():
    if minaraad_exists:
        suite = [
            ztc.FunctionalDocFileSuite(
                'migration.txt',
                test_class=MinaraadFunctionalMigrationTestCase,
                optionflags=OPTIONFLAGS),
            ]
    else:
        suite = []

    return unittest.TestSuite(suite)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
