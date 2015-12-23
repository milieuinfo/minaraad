# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.minaraad import config
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from minaraad.projects.content.base_agendaitem import BaseAgendaItem
from minaraad.projects.content.base_agendaitem import base_agendaitem_schema

schema = atapi.Schema((

    atapi.StringField(
        name='speaker',
        widget=atapi.StringWidget(
            label='Speaker',
            label_msgid='minaraad_label_speaker',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    atapi.StringField(
        name='organisation',
        widget=atapi.StringWidget(
            label='Organisation',
            label_msgid='minaraad_label_organisation',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    atapi.TextField(
        name='summary',
        widget=atapi.TextAreaWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            i18n_domain='minaraad',
        )
    ),

    atapi.DateTimeField(
        name='itemstartdate',
        widget=atapi.CalendarWidget(
            visible=False
        ),
        required=False
    ),

    atapi.DateTimeField(
        name='itemenddate',
        widget=atapi.CalendarWidget(
            visible=False,
        ),
        required=False
    ),

),
)

AgendaItem_schema = getattr(Attachmentsmixin, 'schema', atapi.Schema(())).copy() + \
    base_agendaitem_schema.copy() + \
    schema.copy()


class AgendaItem(Attachmentsmixin, BaseAgendaItem):
    """
    An Agendaitem
    """
    security = ClassSecurityInfo()
    archetype_name = 'AgendaItem'
    portal_type = 'AgendaItem'
    _at_rename_after_creation = True
    schema = AgendaItem_schema


atapi.registerType(AgendaItem, config.PROJECTNAME)
