# -*- coding: utf-8 -*-
#
# File: minaraad.py
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


import patches
patches.patch_all()

from signal import SIGUSR2

from Products.Archetypes import atapi
from Products.Archetypes import listTypes
from Products.CMFCore import utils as cmfutils
from Signals.SignalHandler import SignalHandler
from Signals.Signals import LogfileReopenHandler
from zope.i18nmessageid import MessageFactory

from Products.minaraad import config
from Products.minaraad.utils import email_logger

MinaraadMessageFactory = MessageFactory(u'minaraad')

# Maurits: Is this still necessary. I added ImageAttachementMixin without
# mentioning it here and works fine. Could it be GenericSetup now
# takes care of this?

def initialize(context):
    # imports packages and types for registration
    import content
    import Attachmentsmixin
    content, Attachmentsmixin  # pyflakes

    # Initialize portal content
    content_types, constructors, ftis = atapi.process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types=content_types,
        permission=config.DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors=constructors,
        fti=ftis,
    ).initialize(context)

    loggers = email_logger.handlers
    SignalHandler.registerHandler(SIGUSR2, LogfileReopenHandler(loggers))
