import unittest
import doctest

from Testing import ZopeTestCase as ztc

from MainTestCase import MinaraadFunctionalTestCase

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'email_subscription.txt',
            package='Products.minaraad.tests',
            #test_class=ContentFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE |
                         doctest.REPORT_UDIFF)),
        ztc.FunctionalDocFileSuite(
            'migration.txt',
            test_class=MinaraadFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE |
                         doctest.REPORT_UDIFF)),
        ztc.FunctionalDocFileSuite(
            'themes.txt',
            test_class=MinaraadFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE |
                         doctest.REPORT_UDIFF)),
        ))
