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

__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.minaraad import config


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

ContactPerson_schema = atapi.BaseSchema.copy() + \
    schema.copy()


class ContactPerson(atapi.BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(atapi.BaseContent, '__implements__', ()),)

    # This name appears in the 'add' box
    archetype_name = 'ContactPerson'

    meta_type = 'ContactPerson'
    portal_type = 'ContactPerson'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'ContactPerson.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "ContactPerson"
    typeDescMsgId = 'description_edit_contactperson'

    _at_rename_after_creation = True

    schema = ContactPerson_schema


atapi.registerType(ContactPerson, config.PROJECTNAME)
