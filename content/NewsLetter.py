# -*- coding: utf-8 -*-
#
# File: NewsLetter.py
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
from Products.minaraad.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    DateTimeField(
        name='date',
        index="DateIndex:brains",
        widget=CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        )
    ),

    TextField(
        name='body',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Body',
            label_msgid='minaraad_label_body',
            i18n_domain='minaraad',
        ),
        default_output_type='text/html'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

NewsLetter_schema = BaseFolderSchema.copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class NewsLetter(EmailMixin, BaseFolder):
    """
    A newsletter
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(EmailMixin,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'NewsLetter'

    meta_type = 'NewsLetter'
    portal_type = 'NewsLetter'
    allowed_content_types = ['NewsItem'] + list(getattr(EmailMixin, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'NewsLetter.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "NewsLetter"
    typeDescMsgId = 'description_edit_newsletter'


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

    schema = NewsLetter_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declarePublic('getEmailContentsFromContent')
    def getEmailContentsFromContent(self):
        """
        """
        pass



registerType(NewsLetter, PROJECTNAME)
# end of class NewsLetter

##code-section module-footer #fill in your manual code here
##/code-section module-footer



