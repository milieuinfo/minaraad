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

from Products.minaraad.tests.MainTestCase import MainTestCase
from Products.minaraad.themes import ThemeManager
from zope.component import getMultiAdapter

from zope.publisher.browser import TestRequest
from zope.publisher.browser import setDefaultSkin

THEMES_PROPERTY = [
    '1/Water',
    '2/Klimaat & energie',
    '3/Afval',
    '4/Bodem',
    '5/Europa & Duurzame ontwikkeling',
    '6/Mobiliteit',
    '7/Ruimtelijke ordening',
    '8/Natuur & landbouw',
    '9/NME',
    '10/Milieubegroting',
    '11/Milieuplanning',
    '12/Milieureglementering',
    '13/Instrumenten',
    '14/Milieuhygi\xc3\xabne',
]


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

        tm.themes = [(1, 'abc'), (2, 'def')]
        self.failUnless(tm.themes[0] == (1, 'abc'))
        self.failUnless(tm.themes[1] == (2, 'def'))

        tm.addTheme('duh')
        self.failUnless(tm.themes[2] == (3, 'duh'))

    def test_browserAddTheme(self):
        request = TestRequest()
        setDefaultSkin(request)
        view = getMultiAdapter((self.portal, request),
                               name='minaraad_config.html')

        lastId = max([x[0] for x in view.themeManager.themes])

        request.form['theme_name'] = 'blah'
        view._addTheme()

        self.failUnless(view.themeManager.themes[-1] == (lastId + 1, 'blah'))

    def test_browserSaveThemes(self):
        request = TestRequest()
        setDefaultSkin(request)
        view = getMultiAdapter((self.portal, request),
                               name='minaraad_config.html')

        view.themeManager.themes = [(1, 'a'), (2, 'b'), (3, 'c')]

        request.form['theme_1'] = 'x'
        request.form['theme_3'] = 'z'

        view._saveThemes()

        self.failUnless(view.themeManager.themes == [(1, 'x'),
                                                     (2, 'b'),
                                                     (3, 'z')])

    def test_browserDeleteThemes(self):
        request = TestRequest()
        setDefaultSkin(request)
        view = getMultiAdapter((self.portal, request),
                               name='minaraad_config.html')

        view.themeManager.themes = [(1, 'a'), (2, 'b'), (3, 'c')]

        request.form['theme_1'] = True
        request.form['theme_3'] = True
        view._deleteThemes()
        self.failUnless(view.themeManager.themes == [(2, 'b')])

        request.form['theme_2'] = True
        view._deleteThemes()
        self.failUnless(view.themeManager.themes == [])

    def test_browserThemes(self):
        request = TestRequest()
        setDefaultSkin(request)
        view = getMultiAdapter((self.portal, request),
                               name='minaraad_config.html')

        themes = [(1, 'a'), (2, 'b'), (3, 'c')]
        themesDict = [{'id': id, 'Title': title} for id, title in themes]
        view.themeManager.themes = themes

        self.failUnless(view.themes() == themesDict)

        request.form['form.button.Edit'] = True
        request.form['theme_2'] = 'b'

        self.failUnless(view.themes() == [{'id': 2, 'Title': 'b'}])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testThemes))
    return suite
