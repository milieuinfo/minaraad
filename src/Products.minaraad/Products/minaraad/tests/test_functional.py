import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.minaraad.tests.MainTestCase import MinaraadFunctionalTestCase


def test_suite():
    suite = unittest.TestSuite()

    browser = ztc.ZopeDocFileSuite(
        'browser.txt', package='Products.minaraad.tests',
        test_class=MinaraadFunctionalTestCase,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    suite.addTest(browser)

    return suite
