# File: label.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.0-final
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from Products.minaraad import config

schema=atapi.Schema((
),
)

label_schema = atapi.BaseSchema + \
    schema


class label(atapi.BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'label'
    portal_type = 'label'
    schema = label_schema


atapi.registerType(label, config.PROJECTNAME)
