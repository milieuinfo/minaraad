# -*- coding: utf-8 -*-
#
# File: testMREvent.py
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

from DateTime import DateTime
from Products.minaraad.attendees import AttendeeManager
from Products.minaraad.browser.attendees import AttendeesManagerView
from Products.minaraad.tests.MainTestCase import MainTestCase
from Products.minaraad.tests.utils import load_file
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest


DESCRIPTION = "jaja, een ondertitel"
GOAL = "<p>Doel</p>"
HTMLBODY = "<p>HTML op zijn best</p>"
LOCATION = "Hoogvliet"
STARTDATE = DateTime()
SUBHEADER = "ondertitel"
TESTIMAGE = load_file('test.gif')
TITLE = "title"


class testMREvent(MainTestCase):
    """ test-cases for class(es) MREvent
    """

    def afterSetUp(self):
        """ Initialization of user and MREvent
        """
        self.portal.portal_membership.addMember(
            'manager', 'secret', ['Manager'], [])
        self.login('manager')

        self.portal.evenementen.invokeFactory('MREvent', 'mymrevent')
        self.mrevent = self.portal.evenementen.mymrevent

        testrequest = TestRequest()
        self.view = AttendeesManagerView(self.mrevent, testrequest)

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

        membership = self.portal.portal_membership
        membership.addMember('member', 'secret', ['Member'], [])
        membership.addMember('member2', 'secret', ['Member'], [])

    def test_attendees_export(self):
        # This is actually a test for the
        # browser.attendees.AttendeesManagerView class
        self.loginAsPortalOwner()
        self.portal.evenementen.invokeFactory('MREvent', 'mrevent')
        mrevent = self.portal.evenementen.mrevent

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
            email='johndoe@example.org'
        )

        member.setProperties(**props)

        am = AttendeeManager(mrevent)
        request = self.portal.REQUEST

        request['form.submitted'] = 'exportCSV'
        request['REQUEST_METHOD'] = 'POST'

        view = getMultiAdapter((mrevent, request),
                               name='attendees_view')

        HEADER_FIELDS = (
            "Voornaam", "Achternaam", "Functie / Organisatie", "E-mail")
        headingLine = ''
        for x in HEADER_FIELDS:
            headingLine += '"%s",' % x
        headingLine = headingLine[:-1] + '\n'
        self.assertEquals(view(), headingLine)

        # let's do the actual subscription of our member
        attendee = am.get_from_member(member)
        self.assertTrue(attendee is not None)
        self.assertEqual(attendee.lastname, 'Doe')
        am.add_attendee(attendee)

        lines = view().split('\n')
        self.assertEquals(
            lines[1], '"John","Doe","Doe Enterprises","johndoe@example.org"')

        # let's make some assertions about the response
        self.assertEquals(
            request.RESPONSE.getHeader('content-type'),
            'application/vnd.ms-excel; charset=iso-8859-1')

        self.assertEquals(
            request.RESPONSE.getHeader('content-disposition'),
            'attachment; filename=mrevent-attendees.csv')

    def test_AttendeeRegistration(self):
        """We want to know if members are correctly added and removed as
        attendees.
        """
        attendee1 = self.view.manager.add_attendee(
            lastname='Doe', email='johndoe@example.org')
        self.assertEqual(attendee1.lastname, 'Doe')
        self.assertEqual([attendee1], self.view.manager.attendees())
        attendee2 = self.view.manager.add_attendee(
            lastname='Two', email='johntwo@example.org')
        self.assertEqual([attendee1, attendee2], self.view.manager.attendees())

        self.portal.portal_membership.deleteMembers(
            ['member2'], delete_memberareas=0, delete_localroles=1)
        self.assertEqual([attendee1, attendee2], self.view.manager.attendees())

    def test_Fields_simple(self):
        """ Test if the MREvent has all the required fields
        """

        self.mrevent.Title()           # Titel
        self.mrevent.Description()  # Omschrijving
        self.mrevent.getGoal()         # Doelstelling
        self.mrevent.getSubheader()    # Subkop
        self.mrevent.getLocation()     # Lokatie
        self.mrevent.getStart_time()   # Start tijd
        self.mrevent.get_end_time()    # Eind tijd
        self.mrevent.getContact()      # Contactpersoon

        self.mrevent.setFoto(TESTIMAGE, content_type="image/gif")

        myclass = str(self.mrevent.getFoto().__class__)
        correct = "<class 'plone.app.blob.field.BlobWrapper'>"
        self.failUnless(myclass == correct, 'Value is %s and not %s' %
                        (myclass, correct))

    def test_Fields_properly(self):
        """ Test if getting and setting MREvent fields works.
        """

        self.mrevent.setTitle(TITLE)
        self.mrevent.setDescription(DESCRIPTION)
        self.mrevent.setGoal(GOAL)
        self.mrevent.setSubheader(SUBHEADER)
        self.mrevent.setLocation(LOCATION)
        self.mrevent.setStart_time(STARTDATE)
        self.mrevent.setContact(self.contactperson.UID())
        self.mrevent.setBody(HTMLBODY, text_format="text/html")
        self.mrevent.setFoto(TESTIMAGE, content_type="image/gif")

        self.failUnless(self.mrevent.Title() == TITLE,
                        'Value is %s' % self.mrevent.Title())
        self.failUnless(self.mrevent.getSubheader() == SUBHEADER,
                        'Value is %s' % self.mrevent.getSubheader())
        self.failUnless(self.mrevent.Description() == DESCRIPTION,
                        'Value is %s' % self.mrevent.Description())
        self.failUnless(self.mrevent.getGoal() == GOAL,
                        'Value is %s' % self.mrevent.getGoal())
        self.failUnless(self.mrevent.getLocation() == LOCATION,
                        'Value is %s' % self.mrevent.getLocation())
        self.failUnless(self.mrevent.getStart_time() == STARTDATE,
                        'Value is %s' % self.mrevent.getStart_time())
        self.failUnless(self.mrevent.getBody() == HTMLBODY,
                        'Value is %s' % self.mrevent.getBody())
        self.failUnless(self.mrevent.getContact() == [self.contactperson],
                        'Value is %s' % self.mrevent.getContact())
        myclass = str(self.mrevent.getFoto().__class__)
        correct = "<class 'plone.app.blob.field.BlobWrapper'>"
        self.failUnless(myclass == correct, 'Value is %s and not %s' %
                        (myclass, correct))

    def test_Existance(self):
        """ Test if the MREvent exists within portal_types
        """

        types_ = self.portal.portal_types.objectIds()
        self.failUnless('MREvent' in types_)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMREvent))
    return suite
