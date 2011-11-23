import unittest

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
ptc.setupPloneSite()

import base


def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            'localroles.txt',
            test_class=base.MinaraadFunctionalTestCase,
            optionflags=base.OPTIONFLAGS),
        ztc.FunctionalDocFileSuite(
            'meeting.txt',
            test_class=base.MinaraadFunctionalTestCase,
            optionflags=base.OPTIONFLAGS),
        ztc.FunctionalDocFileSuite(
            'project.txt',
            test_class=base.MinaraadFunctionalTestCase,
            optionflags=base.OPTIONFLAGS),
        ztc.FunctionalDocFileSuite(
            'attachment_numbering.txt',
            test_class=base.MinaraadFunctionalTestCase,
            optionflags=base.OPTIONFLAGS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
