import logging

from Acquisition import aq_parent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from Products.minaraad.config import INITIAL_CHILD_LAYOUT

logger = logging.getLogger('minaraad')


def folder_views(object, event):
    parent = aq_parent(object)
    initial = INITIAL_CHILD_LAYOUT.get(parent.getId(), '')
    if not initial:
        return
    grandparent = aq_parent(parent)
    if IPloneSiteRoot.providedBy(grandparent):
        # Our parent is a child of the site root; okay, we do our
        # stuff.
        logger.info('Setting layout of object %s to %s' %
                    (object.getId(), initial))
        object.setLayout(initial)


def save_theme_name(obj, event):
    """ This event is called everytime an object
    with a theme is updated.
    We store the theme name, so if the theme is deleted in the
    future, we can still display it.
    """
    obj.setThemeName(obj.getThemeName())


def publish_on_save(obj, event):
    """ Event called when saving a FileAttachment object.

    It checks if the 'published' attribute is set to True
    and publish it.

    Otherwise we restrict access.
    """
    wft = getToolByName(obj, 'portal_workflow')
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
