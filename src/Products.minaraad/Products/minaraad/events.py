# -*- coding: utf-8 -*-
from plone import api
import logging


logger = logging.getLogger('minaraad')


def save_theme_name(obj, event=None):
    """This event is called everytime an object with a theme is updated.

    We store the theme name, so if the theme is deleted in the
    future, we can still display it.

    This was used by the OldThemeMixin and will from now on be used by
    the ThemeReferenceMixin.
    """
    obj.setThemeName(obj.getThemeName())


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
