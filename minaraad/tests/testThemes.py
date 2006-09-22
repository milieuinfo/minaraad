# File: testStudy.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.1 svn/devel
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase
from Products.minaraad.themes import ThemeManager
from Products.minaraad.Extensions import AppInstall
from zope.app import zapi

from Products.Five.traversable import FakeRequest
from zope.app.publication.browser import setDefaultSkin


class testThemes(MainTestCase):
    """ test-cases for themes
    """

    def afterSetUp(self):
        """
        """

    def test_themeManager(self):
        """
        """

        tm = ThemeManager(self.portal)
        self.failUnless(len(tm.themes) == len(AppInstall.THEMES_PROPERTY))

        tm.themes = [(1, 'abc'), (2, 'def')]
        self.failUnless(tm.themes[0] == (1, 'abc'))
        self.failUnless(tm.themes[1] == (2, 'def'))
        
        tm.addTheme('duh')
        self.failUnless(tm.themes[2] == (3, 'duh'))

    def test_browserAddTheme(self):
        request = FakeRequest()
        setDefaultSkin(request)
        view = zapi.getView(self.portal, 
                            'minaraad_config.html', 
                            request)
        
        lastId = max([x[0] for x in view.themeManager.themes])
        
        request['theme_name'] = 'blah'
        view._addTheme()
        
        self.failUnless(view.themeManager.themes[-1] == (lastId+1, 'blah'))

    def test_browserSaveThemes(self):
        request = FakeRequest()
        setDefaultSkin(request)
        view = zapi.getView(self.portal, 
                            'minaraad_config.html', 
                            request)

        view.themeManager.themes = [(1, 'a'), (2, 'b'), (3, 'c')]
        
        request['theme_1'] = 'x'
        request['theme_3'] = 'z'
        
        view._saveThemes()
        
        self.failUnless(view.themeManager.themes == [(1, 'x'), 
                                                     (2, 'b'), 
                                                     (3, 'z')])

    def test_browserDeleteThemes(self):
        request = FakeRequest()
        setDefaultSkin(request)
        view = zapi.getView(self.portal, 
                            'minaraad_config.html', 
                            request)

        view.themeManager.themes = [(1, 'a'), (2, 'b'), (3, 'c')]
        
        request['theme_1'] = True
        request['theme_3'] = True
        view._deleteThemes()
        self.failUnless(view.themeManager.themes == [(2, 'b')])
                                                     
        request['theme_2'] = True
        view._deleteThemes()
        self.failUnless(view.themeManager.themes == [])

    def test_browserThemes(self):
        request = FakeRequest()
        setDefaultSkin(request)
        view = zapi.getView(self.portal, 
                            'minaraad_config.html', 
                            request)

        themes = [(1, 'a'), (2, 'b'), (3, 'c')]
        themesDict = [{'id': id, 'Title': title} for id,title in themes]
        view.themeManager.themes = themes

        self.failUnless(view.themes() == themesDict)
        
        request['form.button.Edit'] = True
        request['theme_2'] = 'b'
        
        self.failUnless(view.themes() == [{'id': 2, 'Title': 'b'}])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testThemes))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


