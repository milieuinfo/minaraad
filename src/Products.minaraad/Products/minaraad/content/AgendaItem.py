# -*- coding: utf-8 -*-
#
# File: AgendaItem.py
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
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad import config

from minaraad.projects.content.base_agendaitem import base_agendaitem_schema, BaseAgendaItem

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
