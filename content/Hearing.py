# -*- coding: utf-8 -*-
__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.minaraad.content.MREvent import MREvent
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.config import *

from zope.interface import implements, Interface

schema = Schema((

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

),
)

Hearing_schema = BaseFolderSchema.copy() + \
    getattr(MREvent, 'schema', Schema(())).copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    schema.copy()
Hearing_schema.moveField('theme', after="goal")
Hearing_schema.moveField('mot', after="theme")
# 'goal' (from MREvent) should use a rich text editor on this contenttype.
Hearing_schema['goal'].widget = RichWidget(
    label='Goal',
    label_msgid='minaraad_label_goal',
    i18n_domain='minaraad',
    )
Hearing_schema['goal'].default_output_type = 'text/html'
Hearing_schema['goal'].allowable_content_types = (
    'text/plain', 'text/structured', 'text/html', 'application/msword',)


class IHearing(Interface):
    def getThemesList():
        pass
    def getThemeName():
        pass


class Hearing(MREvent, EmailMixin, BaseFolder):
    """
    A Hearing
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(MREvent,'__implements__',()),) + (getattr(EmailMixin,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Hearing'

    meta_type = 'Hearing'
    portal_type = 'Hearing'
    allowed_content_types = [] + list(getattr(MREvent, 'allowed_content_types', [])) + list(getattr(EmailMixin, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'Hearing.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Hearing"
    typeDescMsgId = 'description_edit_hearing'

    actions =  (
       {'action': "string:${object_url}/email_out",
        'category': "object",
        'id': 'email_out',
        'name': 'E-mail',
        'permissions': ("Modify portal content",),
        'condition': 'python:1'
       },
    )

    _at_rename_after_creation = True
    schema = Hearing_schema
    implements(IHearing)

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

    security.declarePublic('getThemeName')
    def getThemeName(self):
        """
        Get the theme name when it is set
        """
        themeId = self.getTheme()
        themeProps = self.portal_properties.minaraad_properties.getProperty('themes')
        theme = themeProps[themeId-1]
        pos = theme.find('/')
        title = theme[pos+1:]

        return title


registerType(Hearing, PROJECTNAME)
