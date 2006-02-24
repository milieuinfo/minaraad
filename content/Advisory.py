# File: Advisory.py
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
from Products.minaraad.PostMixin import PostMixin
from Products.minaraad.EmailMixin import EmailMixin
from Products.CompoundField.ArrayField import ArrayField
from Products.minaraad.config import *

# additional imports from tagged value 'import'
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    DateTimeField(
        name='date',
        widget=CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        )
    ),

    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    StringField(
        name='body',
        widget=StringWidget(
            label='Body',
            label_msgid='minaraad_label_body',
            i18n_domain='minaraad',
        )
    ),

ArrayField(        FileField(
            name='attachments',
            widget=FileWidget(
                label='Attachments',
                label_msgid='minaraad_label_attachments',
                i18n_domain='minaraad',
            ),
            storage=AttributeStorage()
        ),
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
        relationship='advisorys_contact'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Advisory_schema = ATContentTypeSchema.copy() + \
    getattr(PostMixin, 'schema', Schema(())).copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Advisory_schema['description'].isMetadata = False
##/code-section after-schema

class Advisory(PostMixin, EmailMixin, ATCTContent):
    """
    An advisory
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PostMixin,'__implements__',()),) + (getattr(EmailMixin,'__implements__',()),) + (getattr(ATCTContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Advisory'

    meta_type = 'Advisory'
    portal_type = 'Advisory'
    allowed_content_types = [] + list(getattr(PostMixin, 'allowed_content_types', [])) + list(getattr(EmailMixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    allow_discussion = False
    #content_icon = 'Advisory.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Advisory"
    typeDescMsgId = 'description_edit_advisory'

    schema = Advisory_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Advisory, PROJECTNAME)
# end of class Advisory

##code-section module-footer #fill in your manual code here
##/code-section module-footer



