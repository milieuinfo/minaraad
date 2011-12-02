from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.plone import this
from zope.event import notify


class AttachmentAjax(BrowserView):
    """ Ajax views for attachment related views.

    This was previoudly used on projects (then called the ProjectAjax
    class), but it needs to work when viewing a meeting too.
    """

    @jquery
    def publish_attachment(self):
        attachment_uid = self.request.form.get('att_uid', None)
        if attachment_uid is None:
            return

        published = 'published' in self.request.form
        uid_cat = getToolByName(self.context, 'uid_catalog')

        brains = uid_cat(UID=attachment_uid)
        if not brains:
            return

        attachment = brains[0].getObject()
        attachment.published = published
        notify(ObjectEditedEvent(attachment))

        jq = JQueryProxy()
        # Display the review state: Published or Restricted:
        jq(this).parent().find('.public_attachment').html(
            published and 'Publiek' or 'Besloten')
        return jq
