from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Products.minaraad.utils import email_logger


def buildCSV(context, members, filename='members.csv'):
    portalProperties = getToolByName(context, 'portal_properties')
    siteProperties = portalProperties.site_properties
    charset = siteProperties.getProperty('default_charset')

    out = StringIO()

    fields = (('gender', 'Aanhef'),
              ('firstname', 'Voornaam'),
              ('fullname', 'Achternaam'),
              ('company', 'Organisatie'),
              ('jobtitle', 'Functie'),
              ('street', 'Straat'),
              ('housenumber', 'Huisnummer'),
              ('bus', 'Bus'),
              ('zipcode', 'Postcode'),
              ('city', 'Woonplaats'),
              ('country', 'Land'),
              ('other_country', 'Ander land'),
              ('phonenumber', 'Telefoonnummer'),
              ('email', 'E-mail'))

    for pos, field in enumerate(fields):
        id, title = field

        out.write(u'"%s"' % title)
        if pos < len(fields) - 1:
            out.write(u',')

    out.write(u'\n')

    for member in members:
        for pos, field in enumerate(fields):
            id, title = field
            try:
                value = unicode(member.getProperty(id, ''), charset)
            except UnicodeDecodeError:
                email_logger.warn("UnicodeDecodeError for %s", member.getId())
                value = unicode(member.getProperty(id, ''), charset,
                                errors='replace')
            value = value.replace(u'"', u'""')
            out.write(u'"%s"' % value)

            if pos < len(fields) - 1:
                out.write(u',')

        out.write(u'\n')

    # Excel likes iso-8859-1: when you use 'utf-8' as export charset
    # excel will show wrong characters for names with c-cedille or
    # other such characters.  So we want to send iso-8859-1 here.
    export_charset = 'iso-8859-1'

    response = context.REQUEST.RESPONSE
    response.setHeader('content-type',
                       'application/vnd.ms-excel; charset=%s' % export_charset)
    response.setHeader('content-disposition',
                       'attachment; filename=%s' % filename)

    # Some members have characters that cannot be translated into that
    # charset, like \u2018 which Microsoft is so fond of...  So
    # replace faulty characters with a question mark.
    return out.getvalue().encode(export_charset, 'replace')


def buildAttendeeCSV(context, attendees, filename='attendees.csv'):
    charset = 'utf-8'
    out = StringIO()

    fields = (('firstname', 'Voornaam'),
              ('lastname', 'Achternaam'),
              ('work', 'Functie / Organisatie'),
              ('email', 'E-mail'))

    for pos, field in enumerate(fields):
        id, title = field

        out.write(u'"%s"' % title)
        if pos < len(fields) - 1:
            out.write(u',')

    out.write(u'\n')

    for attendee in attendees:
        for pos, field in enumerate(fields):
            id, title = field
            try:
                value = unicode(getattr(attendee, id, ''), charset)
            except UnicodeDecodeError:
                email_logger.warn("UnicodeDecodeError for %s", attendee.email)
                value = unicode(getattr(attendee, id, ''), charset,
                                errors='replace')
            value = value.replace(u'"', u'""')
            out.write(u'"%s"' % value)

            if pos < len(fields) - 1:
                out.write(u',')

        out.write(u'\n')

    # Excel likes iso-8859-1: when you use 'utf-8' as export charset
    # excel will show wrong characters for names with c-cedille or
    # other such characters.  So we want to send iso-8859-1 here.
    export_charset = 'iso-8859-1'

    response = context.REQUEST.RESPONSE
    response.setHeader('content-type',
                       'application/vnd.ms-excel; charset=%s' % export_charset)
    response.setHeader('content-disposition',
                       'attachment; filename=%s' % filename)

    # Some members have characters that cannot be translated into that
    # charset, like \u2018 which Microsoft is so fond of...  So
    # replace faulty characters with a question mark.
    return out.getvalue().encode(export_charset, 'replace')


def tail(f, n, offset=None):
    """Reads n lines from f with an offset of offset lines.

    From
    http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    avg_line_length = 100
    to_read = n + (offset or 0)

    while True:
        try:
            f.seek(-(avg_line_length * to_read), 2)
        except IOError:
            # woops.  apparently file is smaller than what we want
            # to step back, go to the beginning instead
            f.seek(0)
        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None]
        avg_line_length *= 1.3


class SeeEmailLog(BrowserView):

    def __call__(self):
        try:
            num = int(self.request.get('num', 50))
        except:
            num = 50
        logpath = email_logger.handlers[0].baseFilename
        try:
            logfile = open(logpath)
        except IOError as exc:
            return "Error opening email log file:\n%s" % exc
        try:
            if num == 0:
                # Show all.
                lines = logfile.read().splitlines()
            else:
                lines = tail(logfile, num)
        finally:
            logfile.close()
        linefilter = self.request.get('filter')
        if linefilter:
            # 'Grep' for the filter, for example WARN, ERROR.
            lines = [line for line in lines if linefilter in line]
        lines.insert(0, 'Checked %s lines (?num=%d)' % (num or 'all', num))
        lines.insert(1, 'Filtered on %r (?filter=%s)' % (
            linefilter or 'nothing', linefilter or ''))
        return '\n'.join(lines)


class AttachmentWorkflowHelper(BrowserView):

    def transitions(self, brain):
        current = brain.review_state
        transitions = []
        add = transitions.append
        if current != 'private':
            add(dict(id='retract', name='terugtrekken'))
        if current != 'restricted':
            add(dict(id='restricted_publish', name='besloten publiceren'))
        if current != 'published':
            add(dict(id='publish', name='publiceren'))
        return transitions

    def review_state_title(self, brain):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        return wf_tool.getTitleForStateOnType(
            brain.review_state, brain.portal_type)


HEADER_IMAGE_CSS = """
#portal-header {
    background: url("%s") no-repeat scroll right top #FFFFFF;
    position: relative;
    z-index: 2;
}

"""


class HeaderImageCSS(BrowserView):
    """CSS for header image.

    We want the nearest header.jpg in the acquisition context.  For
    caching it is best to look up the image and return its
    absolute_url, instead of simply loading header.jpg in the current
    context.  It will work, but then the same image will be loaded by
    the browser for lots of different pages.

    This is meant to be used in the rules.xml of the Diazo theme, like this:

    <after css:theme="title" css:content="style" href="@@header-image-css" />

    Because we set the Content-Type header to text/css, diazo will put
    a 'style' tag around it.  Nice.
    """

    def __call__(self):
        image = self.context.restrictedTraverse('header.jpg', None)
        if image is None:
            url = ''
        else:
            url = image.absolute_url()
        self.request.RESPONSE.setHeader('Content-Type', 'text/css')
        return HEADER_IMAGE_CSS % url
