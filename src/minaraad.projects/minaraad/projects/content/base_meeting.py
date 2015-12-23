import logging
from StringIO import StringIO

from zope.interface import implements
from Products.Archetypes import atapi
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from Products.CMFCore.utils import getToolByName

from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.interfaces import IBaseMeeting
from minaraad.projects.utils import (
    smart_int, min_to_days, display_date, human_readable_size)

logger = logging.getLogger('minaraad.projects.content.base_meeting')


base_meeting_schema = atapi.BaseFolderSchema.copy() + atapi.Schema((
    atapi.DateTimeField(
        name='start_time',
        required=True,
        widget=atapi.CalendarWidget(
            label=_(u'label_start_time',
                    default=u'Start'),
        )
    ),
))


class BaseMeeting(atapi.BaseFolder):
    """ This class will be used by all meeting-like
    objects (Meeting, Hearing, Event).
    It provides utilities some utilities:
    - finding agenda items
    - find the end time of the meeting by counting agenda item durations.
    """

    implements(IBaseMeeting)

    def find_items(self):
        """ Returns the list of AgendaItems contained in the meeting.
        """
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog({'path': '/'.join(self.getPhysicalPath()),
                          'portal_type': ['AgendaItem', 'AgendaItemProject']})

        return sorted(brains, key=lambda x: x.getOrder)

    def get_duration(self):
        """ Computes the meeting's duration.
        """
        return smart_int(sum([item.getDuration for item in self.find_items()])
                         / 60)

    def get_end_time(self):
        """ Computes the end date/time of the meeting.
        """
        try:
            return self.getStart_time() + (self.get_duration() / 24.0)
        except TypeError:
            # start time or duration might not be defined and one of
            # them might be None.
            return self.getStart_time()

    def find_items_and_times(self):
        """ Returns a list of tuples: (item, start time, end time)
        """
        start = self.getStart_time()
        items = []

        for item in self.find_items():
            end = start + min_to_days(item.getDuration)
            items.append((item, start, end))
            start = end

        return items

    def manage_delObjects(self, ids, *args, **kwargs):
        """ We override the manage delObjects so we can set
        correct order after deletion.
        """
        # We first check if there is some PDF files in the deleted objects.
        pdf_deleted = False
        for item_id in ids:
            try:
                contains_pdf = self[item_id].contains_pdf()
            except AttributeError:
                # Probably a normal file.
                continue
            if contains_pdf:
                pdf_deleted = True
                break

        # We delete the items.
        base_res = super(BaseMeeting, self).manage_delObjects(ids, *args,
                                                              **kwargs)

        # Now we find the gaps in orders.
        order = -1
        diff = 0

        for item in self.find_items():
            diff += item.getOrder - (order + 1)
            order = item.getOrder

            if diff:
                item.getObject().setOrder(order - diff)

        # If some PDF were deleted, we have to rebuild the concatenated PDFs.
        if pdf_deleted:
            self.generate_pdf()

        return base_res

    def display_date(self):
        return display_date(self.getStart_time())

    def generate_pdf(self):
        """ Checks all items and linked files to generate a huge PDF
        with all files concatenated.
        This action might be quite expensive, so it should not be called
        too often.

        The only reasons when it is called should be:
        - when a FileAttachment is modified (see events.concatenate_pdf)
        - when a FileAttachment is deleted (see
          base_agendaitem.manage_delObjects)
        - when an agenda item is deleted (see base_meeting.manage_delObjects)
        """
        files = []
        for item in self.find_items():
            item = item.getObject()
            for att_id in item.contentIds():
                if item.is_attachment_pdf(att_id):
                    files.append(
                        {'file': StringIO(item[att_id].getFile()),
                         'attachment': '%s/%s' % (item.absolute_url(),
                                                  att_id)})

        if not files:
            self.pdf = None
            return

        self.pdf = PdfFileWriter()

        # Settings when a custom page has to be written.
        font = "Helvetica"
        font_size = 12

        for f in files:
            pdf = PdfFileReader(f['file'])
            if pdf.isEncrypted:
                try:
                    if pdf.decrypt('') == 0:
                        # There is two cases:
                        # - the decrypt method raise an error because
                        #   it can not decrypt
                        # - the decrypt method just returns 0 to tell
                        #   it was not able to decrypt (in this case, we
                        #   raise an exception ourself to create the
                        #   default page)
                        raise Exception('Ho noes, we can not decrypt')
                except:
                    logger.info('Could not decrypt pdf file at "%s"' %
                                f['attachment'])

                    # We generate a simple page to tell the user
                    # we were not able to include this file.
                    text = f['attachment']
                    page = StringIO()
                    my_canvas = canvas.Canvas(page)
                    my_canvas.linkURL(f['attachment'], 0)
                    my_canvas.setFont(font, font_size)
                    my_canvas.drawCentredString(
                        4.0 * inch,
                        8.5 * inch,
                        'Could not integrate file at:')
                    my_canvas.drawCentredString(
                        4.0 * inch,
                        8.0 * inch,
                        text)
                    my_canvas.save()

                    pdf = PdfFileReader(page)

            [self.pdf.addPage(pdf.getPage(page_num))
             for page_num in range(pdf.numPages)]

            if (self.pdf.getNumPages() % 2) == 1 and not f == files[-1]:
                self.pdf.addBlankPage()

    def get_pdf(self):
        """ Returns the PDF generated by 'generate_pdf' as a StringIO.
        """
        try:
            self.pdf
        except AttributeError:
            # Ok, no PDF has been generated yet.
            return None
        if not self.pdf:
            # Previously generated pdf is now empty
            return None
        s = StringIO()
        self.pdf.write(s)
        s.seek(0)
        return s

    def get_pdf_size(self):
        """ Returns the human readable size of the PDF generated.
        """
        pdf = self.get_pdf()
        if pdf is None:
            return '0kB'

        return human_readable_size(pdf.len)
