from zope.component.hooks import getSite
from zope.component import adapts
from zope.interface import implements
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import BooleanField
from Products.CMFCore.utils import getToolByName

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from minaraad.projects.interfaces import IAttachment

from Products.minaraad import MinaraadMessageFactory as _


class PublishedField(ExtensionField, BooleanField):
    """
    """


class FileAttachmentExtender(object):
    adapts(IAttachment)
    implements(ISchemaExtender)

    fields = [
        PublishedField(
            "published",
            widget=BooleanWidget(
                label=_(
                    u'label_attachment_published',
                    default=u'Is published'),
                description=_(
                    u'labelattachment_published_desc',
                    default=(u'Check this box if you want this attachment to '
                             u'be publicly available'))
                    )
                    ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """Get the fields.

        Our extra field should only be available when we are using the
        file_attachment_workflow, so that would be something like this:

        wft = getToolByName(self.context, 'portal_workflow')
        if 'file_attachment_workflow' in [
                wf.id for wf in wft.getWorkflowsFor(self.context)]:
            return self.fields
        return []

        But that does not work when we are being created in the portal
        factory (self.context.isTemporary()).  So we fall back to
        a simple check to see if we are in the digibib.

        """
        portal = getSite()
        if hasattr(portal, 'absolute_url'):
            portal_url = portal.absolute_url
        else:
            # 'portal' can be an instance of
            # Products.Five.metaclass.ValidationView during kss
            # validation...  So try something else then.
            portal_url = getToolByName(self.context, 'portal_url')
        digibib_url = portal_url() + '/digibib'
        if self.context.absolute_url().startswith(digibib_url):
            return self.fields
        return []
