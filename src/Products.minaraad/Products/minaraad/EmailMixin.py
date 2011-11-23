# -*- coding: utf-8 -*-
#
# File: EmailMixin.py
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

schema = atapi.Schema((

    atapi.DateTimeField(
        name='emailSent',
        widget=atapi.CalendarWidget(
            visible=-1,
            label='Emailsent',
            label_msgid='minaraad_label_emailSent',
            i18n_domain='minaraad',
        )
    ),

),
)

EmailMixin_schema = schema.copy()


class AlreadySentError(Exception):
    pass


class EmailMixin:
    """
    """
    security = ClassSecurityInfo()

    allowed_content_types = []
    _at_rename_after_creation = True

    schema = EmailMixin_schema