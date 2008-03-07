# -*- coding: utf-8 -*-
#
# File: testHearing.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.5.0 svn/devel
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

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Test-cases for class(es) Hearing
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.Hearing import Hearing
from Products.minaraad.browser.attendees import AttendeesManagerView

from zope.publisher.browser import TestRequest
##code-section module-beforeclass #fill in your manual code here
from DateTime import DateTime
from Products.minaraad.tests.utils import load_file

from Products.Five.traversable import FakeRequest
from zope.app.publication.browser import setDefaultSkin
from zope.app import zapi

from Products.minaraad.attendees import AttendeeManager


TITLE = "title"
SUBHEADER = "ondertitel"
DESCRIPTION = "jaja, een ondertitel"
GOAL = "Doel"
LOCATION = "Hoogvliet"
THEME = 0
MOT = bool(1)
STARTDATE = DateTime()
ENDDATE = DateTime()
HTMLBODY = "<p>HTML op zijn best</p>"
TESTIMAGE = load_file('test.gif')

##/code-section module-beforeclass

class testHearing(MainTestCase):
    """ test-cases for class(es) Hearing
    """

    ##code-section class-header_testHearing #fill in your manual code here
    ##/code-section class-header_testHearing

    def afterSetUp(self):
        """ Initialization of user and Hearing
        """
        self.portal.portal_membership.addMember('manager','secret',['Manager'],[])
        self.login('manager')

        self.portal.hoorzittingen.invokeFactory('Hearing','myhoorzitting')
        self.hoorzitting = self.portal.hoorzittingen.myhoorzitting
        
        testrequest = TestRequest()
        self.view = AttendeesManagerView(self.hoorzitting, testrequest)

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

        membership = self.portal.portal_membership
        membership.addMember('member', 'secret', ['Member'], [])
        membership.addMember('member2', 'secret', ['Member'], [])

    # from class Hearing:
    def test_getThemesList(self):
        pass

    # from class Hearing:
    def test_getThemeName(self):
        pass

    # from class Hearing:
    def test_email_out(self):
        pass

    # from class EmailMixin:
    def test_email(self):
        """
        """
        #Uncomment one of the following lines as needed
    # from class EmailMixin:
    def test_getEmailBody(self):
        pass

    # from class EmailMixin:
    def test_getSubscriptionId(self):
        pass

    # Manually created methods

    def test_attendees_export(self):
        # This is actually a test for the
        # browser.attendees.AttendeesManagerView class
        self.loginAsPortalOwner()
        self.portal.hoorzittingen.hrz_2006.invokeFactory('Hearing', 'hearing')
        hearing = self.portal.hoorzittingen.hrz_2006.hearing

        self.login('member')
        member = self.portal.portal_membership.getAuthenticatedMember()
        props = dict(
            gender="Yes",
            firstname="John",
            fullname="Doe",
            company="Doe Enterprises",
            street="Doe Street",
            housenumber="23",
            bus="Bus C",
            zipcode="007",
            city="Rotterdam",
            country="The Netherlands",
            )

        member.setProperties(**props)
        
        am = AttendeeManager(hearing)
        request = self.portal.REQUEST

        request['form.submitted'] = 'exportCSV'

        view = zapi.getMultiAdapter((hearing, request),
                                    name='attendees_view')


        HEADER_FIELDS = ("Aanhef","Voornaam","Achternaam","Organisatie",
                         "Functie","Straat","Huisnummer","Bus","Postcode",
                         "Woonplaats","Land","Ander land","Telefoonnummer",
                         "E-mail")
        headingLine = ''
        for x in HEADER_FIELDS:
            headingLine += '"%s",' % x
        headingLine = headingLine[:-1] + '\n'
        self.assertEquals(view(), headingLine)

        # let's do the actual subscription of our member
        am.addMember(member)

        lines = view().split('\n')
        self.assertEquals(lines[1], '"Yes","John","Doe","Doe Enterprises",'
                          '"","Doe Street","23","Bus C","007",'
                          '"Rotterdam","The Netherlands","","",""')

        # let's make some assertions about the response
        self.assertEquals(
            request.RESPONSE.getHeader('content-type'),
            'application/vnd.ms-excel; charset=iso-8859-1'
            )

        self.assertEquals(
            request.RESPONSE.getHeader('content-disposition'),
            'attachment; filename=hearing-attendees.csv'
            )
    def test_Existance(self):
        """ Test if the Hearing exists within portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('Hearing' in types_)

    def test_getThemes(self):
        """
        """
        #Uncomment one of the following lines as needed
    def test_getEmailContentsFromContent(self):
        pass

    def test_getEmailContents(self):
        pass

    def test_themeslist(self):
        """ Test the theme list function in the Hearing content type
        """

        themes = self.hoorzitting.getThemesList()
        self.failUnless(len(themes)>0)
        
    def test_AttendeeRegistration(self):
        """ We want to know if members are correctly added and removed as attendees.
        """
        self.view.manager.addMember('member')
        self.assertEqual(['member'], self.view.manager.attendees())
        self.view.manager.addMember('member2')
        self.assertEqual(['member','member2'], self.view.manager.attendees())

        self.portal.portal_membership.deleteMembers(['member2'], delete_memberareas=0, delete_localroles=1)
        self.assertEqual(['member','member2'], self.view.manager.attendees())
        res = self.view.groupedAttendees()
        self.assertEqual({'council_members': [],
                          'members': [{'memberId': 'member', 'niceName': 'member'}]},
                          res)
        self.assertEqual(len(res['members']), 1)

        self.assertEqual(['member'], self.view.manager.attendees())

        
        
    def test_Fields(self):
        """ Test if the Hearing has all the required fields
        """

        self.hoorzitting.setTitle(TITLE)
        self.hoorzitting.setDescription(DESCRIPTION)
        self.hoorzitting.setGoal(GOAL)
        self.hoorzitting.setSubheader(SUBHEADER)
        self.hoorzitting.setLocation(LOCATION)
        self.hoorzitting.setStartdate(STARTDATE)
        self.hoorzitting.setEnddate(ENDDATE)
        self.hoorzitting.setTheme(THEME)
        self.hoorzitting.setMot(MOT)
        self.hoorzitting.setContact(self.contactperson.UID())
        self.hoorzitting.setBody(HTMLBODY,text_format="text/html")
        self.hoorzitting.setFoto(TESTIMAGE, content_type="image/gif")

        self.failUnless(self.hoorzitting.Title()==TITLE,
                         'Value is %s' % self.hoorzitting.Title())
        self.failUnless(self.hoorzitting.getSubheader()==SUBHEADER,
                         'Value is %s' % self.hoorzitting.getSubheader())
        self.failUnless(self.hoorzitting.getDescription()==DESCRIPTION,
                         'Value is %s' % self.hoorzitting.getDescription())
        self.failUnless(self.hoorzitting.getGoal()==GOAL,
                         'Value is %s' % self.hoorzitting.getGoal())
        self.failUnless(self.hoorzitting.getLocation()==LOCATION,
                         'Value is %s' % self.hoorzitting.getLocation())
        self.failUnless(self.hoorzitting.getStartdate()==STARTDATE,
                         'Value is %s' % self.hoorzitting.getStartdate())
        self.failUnless(self.hoorzitting.getEnddate()==ENDDATE,
                         'Value is %s' % self.hoorzitting.getEnddate())
        self.failUnless(self.hoorzitting.getTheme()==THEME,
                         'Value is %s' % self.hoorzitting.getTheme())
        self.failUnless(self.hoorzitting.getMot()==MOT,
                         'Value is %s' % self.hoorzitting.getMot())
        self.failUnless(self.hoorzitting.getBody()==HTMLBODY,
                         'Value is %s' % self.hoorzitting.getBody())
        self.failUnless(self.hoorzitting.getContact()==[self.contactperson],
                         'Value is %s' % self.hoorzitting.getContact())
        myclass = str(self.hoorzitting.getFoto().__class__)
        correct = "<class 'Products.Archetypes.Field.Image'>"
        self.failUnless(myclass==correct, 'Value is %s and not %s' % (myclass,correct))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHearing))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


