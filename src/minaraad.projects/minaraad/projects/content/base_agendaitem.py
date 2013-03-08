from Acquisition import aq_parent, aq_inner
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from minaraad.projects.interfaces import IAgendaItem
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.utils import min_to_days

base_agendaitem_schema = atapi.OrderedBaseFolderSchema.copy() + atapi.Schema((
    atapi.FloatField(
        name='duration',
        required=True,
        widget=atapi.DecimalWidget(
            label=_(u'label_duration',
                    default=u'Duration'),
            description=_(
                u'desc_duration',
                default=u'Fill in the time in number of minutes.')
            )
        ),

    atapi.IntegerField(
        name='order',
        widget=atapi.IntegerWidget(
            visible=False
            )
        ),
    ))


class BaseAgendaItem(atapi.OrderedBaseFolder):
    """
    """

    implements(IAgendaItem)

    def get_start_time(self):
        """ Returns the item start time.
        """
        meeting = aq_parent(aq_inner(self))
        start_time = meeting.getStart_time()

        for item in meeting.find_items():
            if item.getOrder == self.getOrder():
                break

            try:
                start_time += min_to_days(item.getDuration)
            except TypeError:
                # Duration might not be in the catalog yet, raising a
                # type error while saving get_(start|end)_time in the catalog.
                # In this case, we'll use the object directly.
                item = item.getObject()
                duration = item.getDuration()
                if duration is not None:
                    start_time += min_to_days(duration)

        return start_time

    def get_end_time(self):
        """ Returns the item end time.
        """
        if self.getDuration():
            return self.get_start_time() + min_to_days(self.getDuration())
        return self.get_start_time()

    def setOrder(self, order, recursion=True):
        """ Change the item's order.
        """
        old_order = self.getOrder()
        meeting = aq_parent(self)

        if meeting and old_order is not None and recursion:
            # In this case, we have to edit the other item.

            if old_order > order:
                # We move the item to a previous position.
                items = [i for i in meeting.find_items()
                         if i.getOrder >= order and i.getOrder < old_order]
                modifier = 1
            elif old_order < order:
                # We move it to a further position.
                items = [i for i in meeting.find_items()
                         if i.getOrder <= order and i.getOrder > old_order]
                modifier = - 1
            else:
                # Nothing changed, old_order == order.
                items = []
                modifier = 0

            # We update all items positions.
            for item in items:
                item = item.getObject()
                item.setOrder(item.getOrder() + modifier, recursion=False)

        self.order = order
        self.reindexObject(idxs=['getOrder'])

    def getFiles(self):
        return self.contentValues()

    def is_attachment_pdf(self, att_id):
        """ Tels if the attachment is a PDF file.
        """
        try:
            f = self[att_id].getFile()
            return f.content_type == 'application/pdf'
        except:
            # The attachment might not be a real attachment, or
            # might not exist.
            return False

    def contains_pdf(self):
        """ Returns a boolean telling if one of the attachment is a
        PDF file.
        """
        for att_id in self.contentIds():
            if self.is_attachment_pdf(att_id):
                return True

        return False

    def manage_delObjects(self, ids, *args, **kwargs):
        """ We override this one in order to rebuild the meetings
        PDF concatenation if PDF were deleted.
        """
        pdf_deleted = False
        if isinstance(ids, basestring):
            ids = [ids]
        for att_id in ids:
            if self.is_attachment_pdf(att_id):
                pdf_deleted = True

        base_res = super(BaseAgendaItem, self).manage_delObjects(ids, *args,
                                                                 **kwargs)

        if pdf_deleted:
            aq_parent(self).generate_pdf()

        return base_res

    def can_be_edited(self):
        mtool = getToolByName(self, 'portal_membership')
        return mtool.checkPermission('Modify portal content', self)
