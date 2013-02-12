import unittest
import doctest

from Testing import ZopeTestCase as ztc

from MainTestCase import MinaraadFunctionalTestCase

def test_suite():
    return unittest.TestSuite((
        ztc.FunctionalDocFileSuite(
            'email_subscription.txt',
            test_class=MinaraadFunctionalTestCase,
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
