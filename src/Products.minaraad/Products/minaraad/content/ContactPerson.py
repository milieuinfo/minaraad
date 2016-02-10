# -*- coding: utf-8 -*-
#
# File: ContactPerson.py
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

from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from Products.minaraad import config
from Products.minaraad.interfaces import IContactPerson

schema = atapi.Schema((

    atapi.StringField(
        name='name',
        widget=atapi.StringWidget(
            label='Name',
            label_msgid='minaraad_label_name',
            i18n_domain='minaraad',
        ),
        required=1,
        searchable=1
    ),

    atapi.StringField(
        name='jobtitle',
        widget=atapi.StringWidget(
            label='Jobtitle',
            label_msgid='minaraad_label_jobtitle',
            i18n_domain='minaraad',
        )
    ),

    atapi.StringField(
        name='department',
        widget=atapi.StringWidget(
            label='Department',
            label_msgid='minaraad_label_department',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    atapi.StringField(
        name='email',
        widget=atapi.StringWidget(
            label='Email',
            label_msgid='minaraad_label_email',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    atapi.StringField(
        name='phonenumber',
        widget=atapi.StringWidget(
            label='Phone number',
            label_msgid='minaraad_label_phonenumber',
            i18n_domain='minaraad',
        )
    ),

    atapi.StringField(
        name='linkedin',
        widget=atapi.StringWidget(
            label='LinkedIn Profile URL',
            label_msgid='minaraad_label_linkedin',
            i18n_domain='minaraad',
        )
    ),

),
)

ContactPerson_schema = atapi.BaseSchema.copy() + schema.copy()


class ContactPerson(atapi.BaseContent):
    """
    """
    implements(IContactPerson)
    security = ClassSecurityInfo()
    archetype_name = 'ContactPerson'
    portal_type = 'ContactPerson'
    _at_rename_after_creation = True
    schema = ContactPerson_schema


atapi.registerType(ContactPerson, config.PROJECTNAME)
