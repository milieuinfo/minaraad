# -*- coding: utf-8 -*-
from plone import api
from plone.locking.interfaces import ILockable
from Products.statusmessages.interfaces import IStatusMessage

import logging
import time


logger = logging.getLogger('minaraad')


def save_theme_name(obj, event=None):
    """This event is called everytime an object with a theme is updated.

    We store the theme name, so if the theme is deleted in the
    future, we can still display it.

    This was used by the OldThemeMixin and will from now on be used by
    the ThemeReferenceMixin.
    """
    obj.setThemeTitle(obj.getThemeTitle())


def move_project_advisory(obj, event=None):
    """Move advisory to other theme if project changes its theme.

    This event is called everytime an object with a theme is updated.

    After the initial migration to the new theme folders, some projects
    will need to be linked to a different theme.  When an advisory is
    linked to this project, the theme of the advisory must be updated as
    well.  This means we need to move the advisory to a different theme
    folder.
    """
    # Be defensive in case we are called on an object that is not a Project.
    advisory_getter = getattr(obj, 'get_public_advisory', None)
    if advisory_getter is None:
        return
    advisory = advisory_getter()
    if advisory is None:
        return
    project_theme = obj.getThemeTitle()
    advisory_theme = advisory.getThemeTitle()
    if project_theme == advisory_theme:
        return
    target = obj.getThemeObject()
    lockable = ILockable(advisory)
    if lockable.locked():
        # During migration, we always want to unlock.  During daily use, we
        # want to be a bit more careful.
        if event is not None:
            lock_info = lockable.lock_info()[0]
            lock_age = time.time() - lock_info.get('time', 0)
            if lock_age < (5 * 60):
                IStatusMessage(obj.REQUEST).addStatusMessage(
                    u'Gelinkt advies kon niet verplaatst worden naar nieuw '
                    u'thema: het wordt nu bewerkt door %s.' %
                    lock_info.get('creator'),
                    type='warning')
                return
        lockable.unlock()
        logger.info("Unlocked advisory %s", advisory.title)
    logger.info("Moving advisory %s from %r to %r",
                advisory.title, advisory_theme, project_theme)
    api.content.move(source=advisory, target=target)


def publish_on_save(obj, event):
    """ Event called when saving a FileAttachment object.

    It checks if the 'published' attribute is set to True
    and publish it.

    Otherwise we restrict access.
    """
    wft = api.portal.get_tool(name='portal_workflow')
    try:
        published = obj.published
    except AttributeError:
        # The extra field is not added,
        # so we can not do anything.
        return

    try:
        state = wft.getInfoFor(obj, 'review_state')
    except:
        # The workflow might not have been applied.
        return

    if state == 'published':
        if published:
            return
        action = 'restricted_publish'
    else:
        if not published:
            return
        action = 'publish'

    try:
        wft.doActionFor(obj, action)
    except:
        # Normally this problem should not appear, as we've already
        # checked the state previously.
        # But we might have different placeful workflow policies
        # in the future.
        return
