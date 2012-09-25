from zope.event import notify
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from minaraad.projects import config
from minaraad.projects.interfaces import IMeetingContainer, IMeeting

container_schema = atapi.BaseFolderSchema.copy()


class MeetingContainer(atapi.BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IMeetingContainer)

    _at_rename_after_creation = True
    schema = container_schema

    def exclude_from_nav(self):
        """Always exclude this folder from navigation.
        """
        return True

    def list_meetings(self):
        # List the meetings we are allowed to View.
        catalog = getToolByName(self, 'portal_catalog')
        return sorted(catalog.searchResults(portal_type='Meeting'),
                      key=lambda x: x.getStart_time)

    def _notify_items_modification(self, meeting):
        """ Takes a Meeting object and notify modification
        for all items.
        """
        if meeting and IMeeting.providedBy(meeting):
            for item in meeting.find_items():
                item = item.getObject()

                item.setProject(item.get_previous_project())
                notify(ObjectEditedEvent(aq_inner(item)))

    def manage_pasteObjects(self, *args, **kwargs):
        """ We override the manage_pasteObjects() so we can
        notify modification on all items and so update
        linked projects.
        """
        base = super(MeetingContainer, self).manage_pasteObjects(
            *args, **kwargs)
        for obj in base:
            meeting = self[obj['new_id']]
            self._notify_items_modification(meeting)

        return base

    def manage_clone(self, *args, **kwargs):
        """ We override manage_clone for the same reason we overriden
        manage_pasteObjects
        """
        cloned = super(MeetingContainer, self).manage_clone(*args, **kwargs)
        self._notify_items_modification(cloned)
        return cloned


atapi.registerType(MeetingContainer, config.PROJECTNAME)
