from DateTime import DateTime
import logging
from smtplib import SMTPException
import pkg_resources
import socket
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite

zope2_egg = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('Zope2'))
USE_SECURE_SEND = True
if zope2_egg and (zope2_egg.parsed_version >=
                  pkg_resources.parse_version('2.12.3')):
    USE_SECURE_SEND = False

logger = logging.getLogger('minaraad.projects.utils')


def smart_int(number):
    """ Returns an integer when needed, a float otherwise.

    >>> smart_int(2)
    2

    >>> smart_int(2.5)
    2.5
    """
    inumber = int(number)
    if inumber == number:
        return inumber
    return number


def min_to_days(m):
    try:
        return m / 1440
    except TypeError:
        return 0


def prepend_zero(n):
    """ Just a helper to get small numbers displayed correctly.

    >>> prepend_zero(0)
    '00'

    >>> prepend_zero(7)
    '07'

    >>> prepend_zero(10)
    '10'
    """
    return '%s%s' % (n < 10 and '0' or '',
                     n)


def display_date(d):
    """ Displays the date the dutch way.

    >>> from DateTime import DateTime
    >>> display_date(DateTime(2010, 8, 3))
    '03-08-2010'
    """
    return '%s-%s-%s' % (prepend_zero(d.day()),
                         prepend_zero(d.month()),
                         prepend_zero(d.year()))


def display_hours(h):
    """ Displays the hours.

    >>> from DateTime import DateTime
    >>> display_hours(DateTime(2010, 8, 3, 15, 30))
    '15:30'
    """
    return '%s:%s' % (prepend_zero(h.hour()),
                      prepend_zero(h.minute()))


def datetime_diff_minutes(start, end):
    """ Computes the difference between two DateTime
    objects in minutes.

    We need this helper because multiplying by 1440 and
    then rounding can give weird results.
    Note: this seems to be fixed with Python 2.6. We keep the
    method for safety reasons.

    >>> d1 = DateTime(2010, 2, 9, 13, 20)
    >>> d2 = DateTime(2010, 2, 9, 14, 00)

    >>> datetime_diff_minutes(d1, d2)
    40

    It works over different hours:
    >>> datetime_diff_minutes(
    ...     DateTime(2010, 1, 1, 8, 30),
    ...     DateTime(2010, 1, 1, 16, 00))
    450

    Or over days:
    >>> datetime_diff_minutes(
    ...     DateTime(2010, 1, 1, 15, 30),
    ...     DateTime(2010, 1, 2, 8, 0))
    990

    Or over years:
    >>> datetime_diff_minutes(
    ...     DateTime(2009, 12, 31, 23, 30),
    ...     DateTime(2010, 1, 1, 0, 15))
    45

    >>> datetime_diff_minutes(
    ...     DateTime(2009, 12, 30, 23, 30),
    ...     DateTime(2010, 1, 1, 0, 15))
    1485

    """
    def simple_date(d):
        return DateTime(d.year(), d.month(), d.day())

    return 1440 * int(simple_date(end) - simple_date(start)) + \
           60 * (end.hour() - start.hour()) + \
           end.minute() - start.minute()


def human_readable_size(size):
    """ Return the size in bytes to a human readable format.
    Inspired by Products.CMFPlone.skins.plone_scripts.getObjSize

    >>> human_readable_size(0)
    '0 B'

    >>> human_readable_size(900)
    '0.9 kB'

    >>> human_readable_size(12000)
    '11.7 kB'

    >>> human_readable_size(12000000)
    '11.4 MB'

    >>> human_readable_size(12000000000)
    '11.2 GB'
    """
    const = {'kB': 1024.0,
             'MB': 1024.0 * 1024,
             'GB': 1024.0 * 1024 * 1024}

    for order in ('GB', 'MB', 'kB'):
        if (size / const[order]) < 0.8:
            continue

        return '%.1f %s' % (size / const[order], order)

    return '%s B' % size


def send_email(mto, mfrom, title, content):
    portal = getSite()
    mail_host = getToolByName(portal, 'MailHost', None)

    try:
        if USE_SECURE_SEND:
            mail_host.secureSend(message=content,
                                 mto=mto,
                                 mfrom=mfrom,
                                 subject=title,
                                 charset='utf-8')
        else:
            mail_host.send(message=content,
                           mto=mto,
                           mfrom=mfrom,
                           subject=title,
                           charset='utf-8',
                           immediate=True)

    except (socket.error, SMTPException):
        logger.warn('Could not send email to %s with subject %s',
                    mto, title)


def getEndOfMonth(year, month):
    """Get the last second of the last day of this month

    Taken from Products.eXtremeManagement.

    First some normal months.

    >>> getEndOfMonth(2007, 1)
    DateTime('2007/01/31 23:59:59 GMT+1')
    >>> getEndOfMonth(2007, 4)
    DateTime('2007/04/30 23:59:59 GMT+2')

    Of course February needs extra testing.

    >>> getEndOfMonth(2007, 2)
    DateTime('2007/02/28 23:59:59 GMT+1')

    2008 is a leap year.

    >>> getEndOfMonth(2008, 2)
    DateTime('2008/02/29 23:59:59 GMT+1')

    """
    if month in (1, 3, 5, 7, 8, 10, 12):
        day = 31
    elif month == 2:
        if DateTime(year, 1, 1).isLeapYear():
            day = 29
        else:
            day = 28
    else:
        day = 30
    return DateTime.latestTime(DateTime(year, month, day))


def link_project_and_advisory(project, advisory):
    #project.advisory_uid = advisory.UID()
    #advisory.project_uid = project.UID()
    # We have added a referenceField on the advisory:
    advisory.setProject(project.UID())


def is_advisory_request(doc):
    if doc.Title().lower() == 'adviesvraag':
        return True
    # adviesvraag.pdf:
    if doc.getId().lower().split('.')[0] == 'adviesvraag':
        return True
    return False


def create_attachment(context, document, published=True):
    # Create an attachment.
    try:
        doc_file = document.getFile()
    except AttributeError:
        return
    attachment_id = context.generateUniqueId('FileAttachment')
    context.invokeFactory('FileAttachment', id=attachment_id)
    attachment = context[attachment_id]
    # For some reason the file field needs to be
    # handled separately.
    attachment.setFile(doc_file)
    fields = dict(title=document.Title(), published=published)
    attachment.processForm(values=fields)
    # processForm may have caused a rename
    attachment_id = attachment.getId()
    logger.info("Created a %s attachment with id %s.",
                published and 'published' or 'private', attachment_id)
    return attachment
