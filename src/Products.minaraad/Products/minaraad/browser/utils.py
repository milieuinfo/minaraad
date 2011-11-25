import logging
import os
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

# Arrange logging, for use by other modules.
email_logger = logging.getLogger('minaraad_email')
# Also log these messages to a separate file
# XXX this may be possible through zope.conf too but I can't figure out
logbase = os.environ.get('MINARAAD_LOG_PATH')
if not logbase:
    logbase = os.environ.get('INSTANCE_HOME') + '/log'
logpath = '%s/minaraad_email.log' % logbase
# Get rid of any duplicate slashes:
logpath = os.path.realpath(logpath)
hdlr = logging.FileHandler(logpath)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
email_logger.addHandler(hdlr)


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


def tail(f, n, offset=None):
    """Reads n lines from f with an offset of offset lines.

    From
    http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    avg_line_length = 100
    to_read = n + (offset or 0)

    while 1:
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
            lines = int(self.request.get('lines', 50))
        except:
            lines = 50
        try:
            logfile = open(logpath)
            lines = tail(logfile, lines)
        finally:
            logfile.close()
        return '\n'.join(lines)
