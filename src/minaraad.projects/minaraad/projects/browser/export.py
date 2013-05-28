from operator import itemgetter
from StringIO import StringIO

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.i18n import translate

from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.widgets import PARTICIPANT_PRESENT, \
    PARTICIPANT_EXCUSED, PARTICIPANT_ABSENT
from minaraad.projects.utils import getEndOfMonth


class ExportStatisticsView(BrowserView):
    """Monthly/quarterly statistics downloadable as csv.
    """

    # Set some defaults.
    starting_year = 2010
    values = {}
    headers = []
    rows = []
    start = None
    end = None
    preview = False

    def available_statistics(self):
        # Each available report/statistic must be a tuple of id and
        # title.  The id must be the same as the method name in this
        # view that should be called when this statistic is selected.
        # Ids MUST start with 'report_' as a minor security measure.
        available = [
            ('report_attendance_summary', _(u"Attendance Summary")),
            # Here is an old one that may be handy for testing the
            # statistics selection:
            #('report_attendance_per_meeting', _(u"Attendance Per Meeting")),
            ]

        statistics = []
        statistic = self.request.get('export_statistic', '')
        for report_id, report_title in available:
            d = {'id': report_id, 'value': report_id, 'selected': None}
            if report_id == statistic or len(available) == 1:
                d['selected'] = 1
            d['title'] = translate(report_title, context=self.request)
            statistics.append(d)
        # Sort by title.
        statistics = sorted(statistics, key=itemgetter('title'))
        if len(available) != 1:
            # If we want a select dropdown we must add this at the top:
            if statistic:
                statistics.insert(0,
                    {'id': '--', 'value': '--', 'selected': None,
                     'title': '--'})
            else:
                statistics.insert(0,
                    {'id': '--', 'value': '--', 'selected': 1,
                     'title': '--'})

        return statistics

    def _set_dates(self):
        form_submitted = self.request.get('form_submitted', '')
        month = self.request.get('export_month', '')
        quarter = self.request.get('export_quarter', '')
        year = self.request.get('export_year', '')
        today = DateTime()
        # Might as well start with the year.
        try:
            year = int(year)
        except ValueError:
            year = today.year()
        else:
            if year < self.starting_year:
                year = today.year()

        # Now see if a month was specified.
        try:
            month = int(month)
        except ValueError:
            if form_submitted:
                # Likely '--' was submitted as value.
                month = 0
            else:
                # On initial display set the current month.
                month = today.month()
        else:
            # Note that we can handle month=0 just fine: we treat it
            # as not selected.
            if month < 0 or month > 12:
                month = today.month()

        # Alternatively, not a month, but a quarter will have been
        # specified.
        try:
            quarter = int(quarter)
        except ValueError:
            quarter = 0
        else:
            if quarter < 0 or quarter > 4:
                quarter = 0

        # Now the idea is: only when a valid quarter has been filled
        # in, do we use the quarter, else when a valid month has been
        # filled in we will use the month, else we will use the entire
        # year.

        if not form_submitted:
            # Pick the current month on initial display.
            start = DateTime(year, month, 1)
            end = getEndOfMonth(year, month)
        elif quarter:
            # 1: 1-3
            # 2: 4-6
            # 3: 7-9
            # 4: 10-12
            end_month = 3 * quarter
            start_month = end_month - 2
            start = DateTime(year, start_month, 1)
            end = getEndOfMonth(year, end_month)
        elif month:
            start = DateTime(year, month, 1)
            end = getEndOfMonth(year, month)
        else:
            start = DateTime(year, 1, 1)
            end = getEndOfMonth(year, 12)

        # Get some nice values for the months and years to iterate
        # over in the template.
        date_components_support_view = getMultiAdapter(
            (self.context, self.request), name='date_components_support')
        values = date_components_support_view.result(
            start, 0, self.starting_year, today.year())

        # Add nice values for the quarters as well.
        quarters = []
        if quarter:
            quarters.append(
                {'id': '--', 'value': '--', 'selected': None, 'title': '--'})
        else:
            quarters.append(
                {'id': '--', 'value': '--', 'selected': 1, 'title': '--'})
        for x in range(1, 5):
            d = {'id': x, 'value': x, 'selected': None}
            if x == quarter:
                d['selected'] = 1
            d['title'] = translate(
                _(u'quarter_name',
                  default=u'Quarter ${number}',
                  mapping={'number': x}),
                context=self.request)
            quarters.append(d)
        values['quarters'] = quarters
        if quarter or (form_submitted and not month):
            # We are using the quarter or the full year, so we clear
            # the month values by giving an inputvalue of None.
            clear_month_values = date_components_support_view.result(
                None, 0, self.starting_year, today.year())
            values['months'] = clear_month_values['months']

        # Store the values on the view so the template can use them.
        self.values = values
        self.start = start
        self.end = end

    def __call__(self):
        self._set_dates()
        if self.request.form.get('form_submitted'):
            # Determine which report to generate.
            statistic = self.request.get('export_statistic', '')
            if statistic.startswith('report_') and hasattr(self, statistic):
                generate = getattr(self, statistic)
                generate()
                if self.request.form.get('export'):
                    # Generate CSV from the headers and rows that have been
                    # set.
                    return self.buildCSV()
                if self.request.form.get('preview'):
                    self.preview = True
        return self.index()

    def report_attendance_summary(self):
        """Attendence summary.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            portal_type='Meeting',
            review_state='past',
            getStart_time={'query': [self.start, self.end],
                           'range': 'minmax'},
            )
        meetings = [brain.getObject() for brain in brains]
        users = {}
        headers = [u'#', u'Naam', u'Organisatie', u'Aanwezig',
                   u'Verontschuldigd', u'Afwezig']
        for meeting in meetings:
            for user, attendance in meeting.getParticipants():
                if user not in users:
                    users[user] = dict(present=0, excused=0, absent=0)
                if attendance == PARTICIPANT_PRESENT:
                    users[user]['present'] += 1
                elif attendance == PARTICIPANT_EXCUSED:
                    users[user]['excused'] += 1
                elif attendance == PARTICIPANT_ABSENT:
                    users[user]['absent'] += 1

        mtool = getToolByName(self.context, 'portal_membership')
        rows = []
        for user, data in users.items():
            member = mtool.getMemberById(user)
            if member:
                names = [safe_unicode(member.getProperty('firstname', '')),
                         safe_unicode(member.getProperty('fullname'))]
                fullname = u' '.join([name for name in names if name])
                company = safe_unicode(member.getProperty('company', ''))
            else:
                # We used to allow these too, but they are not wanted
                # anymore, especially with the addition of the
                # otherInvitees datagrid field.
                #fullname = user
                #company = ''
                continue
            row = [fullname, company, data['present'], data['excused'],
                   data['absent']]
            rows.append(row)

        self.headers = headers
        rows.sort()
        # Add row number in first column.
        for index, row in enumerate(rows):
            row.insert(0, index + 1)
        self.rows = rows

    def report_attendance_per_meeting(self):
        """Attendence per meeting.

        XXX This is an old report, for the moment kept as example code
        for future reports.
        """
        # This does things slightly differently, which may be handy to
        # keep for the moment.
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            portal_type='Meeting',
            review_state='past',
            getStart_time={'query': [self.start, self.end],
                           'range': 'minmax'},
            )
        meetings = [brain.getObject() for brain in brains]
        users = {}
        headers = [u'Naam', u'Organisatie']
        ploneview = getMultiAdapter((self.context, self.request), name='plone')

        for index, meeting in enumerate(meetings):
            group = meeting.getResponsible_group()
            date = ploneview.toLocalizedTime(meeting.getStart_time())
            title = u"%s %s" % (group, date)
            headers.append(title)
            for user, attendance in meeting.getParticipants():
                if user not in users:
                    users[user] = {}
                users[user][index] = attendance

        participation_mapping = {
            PARTICIPANT_PRESENT: 'P',
            PARTICIPANT_EXCUSED: 'E',
            PARTICIPANT_ABSENT: 'A',
            }
        mtool = getToolByName(self.context, 'portal_membership')
        rows = []
        for user, data in users.items():
            member = mtool.getMemberById(user)
            fullname = member and member.getProperty('fullname') or user
            company = member and member.getProperty('company', '') or ''
            row = [fullname, company]
            for col in range(len(meetings)):
                # Add the attendence, if this user was invited for
                # this meeting.
                attendance = data.get(col, '')
                attendance_sign = participation_mapping.get(attendance, '-')
                row.append(attendance_sign)
            rows.append(row)

        self.headers = headers
        self.rows = rows

    def buildCSV(self, filename='export_attendance.csv'):
        # We might want to use the standard csv module, but this method is
        # taken and adapted from Products.minaraad, so that is probably a
        # fine base as well.

        # Start with a header line.
        out = StringIO()
        out.write(u','.join(self.headers))
        out.write(u'\n')

        for row in self.rows:
            for pos, value in enumerate(row):
                value = safe_unicode(value)
                if isinstance(value, unicode):
                    value = value.replace(u'"', u'""')
                    value = u'"%s"' % value
                else:
                    # Probably an integer
                    value = u"%s" % value
                out.write(value)
                if pos < len(row) - 1:
                    out.write(u',')
            out.write(u'\n')

        # Excel likes iso-8859-1: when you use 'utf-8' as export charset
        # excel will show wrong characters for names with c-cedille or
        # other such characters.  So we want to send iso-8859-1 here.
        # OpenOffice selects utf-8 by default though.
        export_charset = 'iso-8859-1'

        response = self.request.RESPONSE
        response.setHeader('content-type',
                           'application/vnd.ms-excel; charset=%s' %
                           export_charset)
        response.setHeader('content-disposition',
                           'attachment; filename=%s' % filename)

        # There may be characters that cannot be translated into our
        # charset, like \u2018 which Microsoft is so fond of...  So
        # replace faulty characters with a question mark.
        return out.getvalue().encode(export_charset, 'replace')
