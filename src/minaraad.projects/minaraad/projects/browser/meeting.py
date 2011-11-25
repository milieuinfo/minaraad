from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from jquery.pyproxy.plone import jquery, JQueryProxy

from minaraad.projects.interfaces import IAgendaItemProject


class MeetingView(BrowserView):
    """ Default view of a Meeting.
    """

    def clean_temporary_objects(self):
        # We delete potentialially left temporary attachments
        # or agenda items.
        to_delete = []
        for item in self.context.contentValues():
            if not IAgendaItemProject.providedBy(item):
                continue

            if item.getIn_factory():
                to_delete.append(item.id)
                continue

            view = item.restrictedTraverse('@@edit_agenda_item')
            view.delete_temp_attachments()

        self.context.manage_delObjects(to_delete)

    def __call__(self):
        self.clean_temporary_objects()
        return self.index()


class MeetingOrderingView(MeetingView):
    """ This view allows to manage order of the agenda items.
    """

    def __call__(self):
        form = self.request.form
        if 'uid' not in form:
            return self.index()

        uid_cat = getToolByName(self.context, 'uid_catalog')
        brains = uid_cat(UID=form['uid'])

        if not brains:
            return

        item = brains[0].getObject()
        if 'up' in form:
            modifier = -1
        else:
            modifier = 1

        item.setOrder(item.getOrder() + modifier)

        # The order changed, we update the PDF file.
        self.context.generate_pdf()
        return self.index()


class MeetingPdfView(MeetingView):
    """ View used to download the PDF file concatenating
    all PDF for the meeting.
    """

    def __call__(self):
        pdf = self.context.get_pdf()
        if not pdf:
            return

        filename = 'meeting.pdf'
        self.request.response.setHeader('Cache-Control',
                                        'no-store, no-cache, must-revalidate')
        self.request.response.setHeader('Content-Type',
                                        'application/pdf')
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename="%s"' % filename)
        self.request.response.write(pdf.read())


class MeetingAjax(MeetingView):
    @jquery
    def meeting_order_changed(self):
        form = self.request.form
        catalog = getToolByName(self.context, 'portal_catalog')

        jq = JQueryProxy()
        uid = form.get('uid', None)
        try:
            position = int(form.get('position', None))
        except:
            position = None

        if uid is None or position is None:
            # We need both position and uid.
            return jq

        # First we find the item.
        items = self.context.find_items()
        item = None

        for i in items:
            if i.UID == uid:
                item = i
                break

        if item is None:
            # The UID does not correspond to
            # an item of the meeting.
            return jq

        # We set the correct order.
        obj = item.getObject()
        obj.setOrder(position)

        # The order changed, we update the PDF file.
        self.context.generate_pdf()

        # We generate the new table content.
        att_count = 1

        for item in self.context.find_items_and_times():
            it_obj = item[0].getObject()
            it_obj.attachment_start = att_count

            jq('#%s span.agendaItemTimes' % item[0].UID).html(
                '%s tot %su' % (item[1].TimeMinutes(),
                                item[2].TimeMinutes()))

            attachments = catalog.searchResults(
                portal_type='FileAttachment',
                path='/'.join(it_obj.getPhysicalPath()))
            for att in attachments:
                jq('#att_%s' % att.UID).html('Bijlage %s: %s' % (
                    att_count, att.Title))
                att_count += 1

        return jq
