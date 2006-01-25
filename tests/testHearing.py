# File: testHearing.py
# 
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.0-final 
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Rocky Burt <r.burt@zestsoftware.nl>'''
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# test-cases for class(es) Hearing
#
import os, sys
from Testing import ZopeTestCase
from Products.minaraad.tests.MainTestCase import MainTestCase
# import the tested classes
from Products.minaraad.content.Hearing import Hearing

##code-section module-beforeclass #fill in your manual code here
##/code-section module-beforeclass


class testHearing(MainTestCase):
    """ test-cases for class(es) Hearing
    """

    ##code-section class-header_testHearing #fill in your manual code here
    ##/code-section class-header_testHearing

    def afterSetUp(self):
        """
        """
        pass


    # from class EmailMixin:
    def test_email(self):
        """
        """
        #Uncomment one of the following lines as needed
        ##self.loginAsPortalOwner()
        ##o=EmailMixin('temp_EmailMixin')
        ##self.folder._setObject('temp_EmailMixin', o)
        pass



    # Manually created methods

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHearing))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer


if __name__ == '__main__':
    framework()


