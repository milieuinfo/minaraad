# File: Hearing.py
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

    StringField(
        name='subheader',
        widget=StringWidget(
            label='Subheader',
            label_msgid='minaraad_label_subheader',
            i18n_domain='minaraad',
        )
    ),

    TextField(
        name='goal',
        widget=TextAreaWidget(
            label='Goal',
            label_msgid='minaraad_label_goal',
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

    StringField(
        name='location',
        widget=StringWidget(
            label='Location',
            label_msgid='minaraad_label_location',
            i18n_domain='minaraad',
        )
    ),

    IntegerField(
        name='theme',
        widget=SelectionWidget(
            label='Theme',
            label_msgid='minaraad_label_theme',
            i18n_domain='minaraad',
        ),
        vocabulary='getThemesList'
    ),

    BooleanField(
        name='mot',
        widget=BooleanWidget(
            description="Check this option if the hearing is a MOT.",
            label='Mot',
            label_msgid='minaraad_label_mot',
            description_msgid='minaraad_help_mot',
            i18n_domain='minaraad',
        )
    ),

    DateTimeField(
        name='startdate',
        index="DateIndex:brains",
        widget=CalendarWidget(
            label='Startdate',
            label_msgid='minaraad_label_startdate',
            i18n_domain='minaraad',
        ),
        required=1
    ),

    DateTimeField(
        name='enddate',
        widget=CalendarWidget(
            label='Enddate',
            label_msgid='minaraad_label_enddate',
            i18n_domain='minaraad',
        ),
        required=1
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
        relationship='hearings_contact'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Hearing_schema = BaseFolderSchema.copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Hearing(EmailMixin, BaseFolder):
    """
    A Hearing
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(EmailMixin,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Hearing'

    meta_type = 'Hearing'
    portal_type = 'Hearing'
    allowed_content_types = ['AgendaItem'] + list(getattr(EmailMixin, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    allow_discussion = False
    #content_icon = 'Hearing.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Hearing"
    typeDescMsgId = 'description_edit_hearing'

    _at_rename_after_creation = True

    schema = Hearing_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getThemesList')
    def getThemesList(self):
        """
        Get themes from minaraad properties
        """
        props = self.portal_properties.minaraad_properties
        themeProps = props.getProperty('themes')
        themes = []
        for x in themeProps:
            pos = x.find('/')
            id = x[:pos]
            title = x[pos+1:]
            themes.append({'id':id, 'title':title})
        
        dlist = DisplayList(
                   tuple([(theme['id'], theme['title']) for theme in themes ])
                )

        return dlist


registerType(Hearing, PROJECTNAME)
# end of class Hearing

##code-section module-footer #fill in your manual code here
##/code-section module-footer



