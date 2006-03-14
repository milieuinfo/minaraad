# -*- coding: utf-8 -*-
#
# File: Pressrelease.py
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
from Products.Archetypes.atapi import *
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='subheader',
        widget=StringWidget(
            label='Subheader',
            label_msgid='minaraad_label_subheader',
            i18n_domain='minaraad',
        )
    ),

    ReferenceField(
        name='contact',
        widget=ReferenceWidget(
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson',),
        multiValued=1,
        relationship='pressrelease_contact'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Pressrelease_schema = getattr(EmailMixin, 'schema', Schema(())).copy() + \
    getattr(Attachmentsmixin, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Pressrelease(EmailMixin, Attachmentsmixin):
    """
    A pressrelease
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(EmailMixin,'__implements__',()),) + (getattr(Attachmentsmixin,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Pressrelease'

    meta_type = 'Pressrelease'
    portal_type = 'Pressrelease'
    allowed_content_types = [] + list(getattr(EmailMixin, 'allowed_content_types', [])) + list(getattr(Attachmentsmixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    allow_discussion = False
    #content_icon = 'Pressrelease.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Pressrelease"
    typeDescMsgId = 'description_edit_pressrelease'


    actions =  (


       {'action': "string:${object_url}/email_out",
        'category': "object",
        'id': 'email_out',
        'name': 'E-mail',
        'permissions': ("View",),
        'condition': 'python:1'
       },


    )

    _at_rename_after_creation = True

    schema = Pressrelease_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Pressrelease, PROJECTNAME)
# end of class Pressrelease

##code-section module-footer #fill in your manual code here
##/code-section module-footer



