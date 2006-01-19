# File: Advisory.py
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


from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.minaraad.EmailMixin import EmailMixin


# additional imports from tagged value 'import'
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.AttachmentField.AttachmentField import AttachmentField

from Products.minaraad.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    TextField(
        name='htmlBody',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        allow_file_upload=False,
        widget=RichWidget(
            label='Htmlbody',
            label_msgid='minaraad_label_htmlBody',
            description_msgid='minaraad_help_htmlBody',
            i18n_domain='minaraad',
        ),
        default_output_type='text/html'
    ),

    TextField(
        name='textBody',
        widget=TextAreaWidget(
            label='Textbody',
            label_msgid='minaraad_label_textBody',
            description_msgid='minaraad_help_textBody',
            i18n_domain='minaraad',
        )
    ),

    FileField(
        name='pdfFile',
        widget=FileWidget(
            label='Pdffile',
            label_msgid='minaraad_label_pdfFile',
            description_msgid='minaraad_help_pdfFile',
            i18n_domain='minaraad',
        ),
        storage=AttributeStorage(),
        multiValued=True
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Advisory_schema = ATContentTypeSchema.copy() + \
    getattr(EmailMixin,'schema',Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Advisory(EmailMixin,ATCTContent):
    """
    An advisory
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(EmailMixin,'__implements__',()),) + (getattr(ATCTContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name = 'Advisory'

    meta_type = 'Advisory'
    portal_type = 'Advisory'
    allowed_content_types = [] + list(getattr(EmailMixin, 'allowed_content_types', []))
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

registerType(Advisory,PROJECTNAME)
# end of class Advisory

##code-section module-footer #fill in your manual code here
##/code-section module-footer



