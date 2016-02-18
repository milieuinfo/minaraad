from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from textwrap import dedent

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView

from Products.minaraad.utils import email_logger as logger

LIMIT_MINUTES = 30


class DictLike(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)


def fixRelativeUrls(xml, portal_url):
    return xml.replace('./resolveUid', portal_url + '/resolveUid')


class RenderedContent(dict):

    def __init__(self, dict=None):
        if dict is None:
            dict = {'text/plain': u'', 'text/html': u''}
        super(RenderedContent, self).__init__(dict)

    def __add__(self, other):
        self['text/plain'] += u'\n%s' % (safe_unicode(other['text/plain']), )
        self['text/html'] += safe_unicode(other['text/html'])
        return self


class EmailRenderer(object):
    'Base for email renderer adapters'

    # methods to overwrite

    def __init__(self, context):
        self.context = context

    def render(self, attendee):
        'Implement rendering the email.'
        raise 'Unimplemented'

    # helpers for rendering

    def renderFromTemplate(self, email_template, **kwargs):
        """
        Return both plain and html versions (a dict with keys
        'text/plain' and 'text/html') of an appropriate email template.
        Default implementation will cook the template from schema field
        emailTemplate.
        """
        context = aq_inner(self.context)
        portal_url_tool = getToolByName(context, 'portal_url')
        portal_url = portal_url_tool()
        portal = portal_url_tool.getPortalObject()
        portal_transforms = getToolByName(portal, 'portal_transforms')
        plone_utils = getToolByName(portal, 'plone_utils')
        charset = plone_utils.getSiteEncoding()

        cooked = email_template.pt_render(extra_context=kwargs)
        cooked = fixRelativeUrls(cooked, portal_url)
        # cooked should be unicode already, but let's make sure it is.
        cooked = safe_unicode(cooked, encoding=charset)
        # Unfortunately portal_transforms (or lynx_dump) expects an
        # encoded string.
        plain = portal_transforms('lynx_dump', cooked.encode(charset))
        plain = safe_unicode(plain, encoding=charset)

        body = RenderedContent({
            'text/html': cooked,
            'text/plain': plain,
        })

        return body

    def renderFromText(self, text):
        """
        Return both plain and html versions (a dict with keys
        'text/plain' and 'text/html') of a given text.
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        charset = plone_utils.getSiteEncoding()
        text = safe_unicode(text, encoding=charset)
        body = RenderedContent({
            'text/plain': text,
            'text/html': dedent(u'''\
                                <br />
                                <br />
                                <br />
                                %s
                                ''' % text),
        })
        return body


class EmailNotify(BrowserView):
    'General email notification'

    EmailRenderer = EmailRenderer

    def email(self, renderer, attendees=None):
        """Send email to attendees, using renderer.
        """
        if attendees is None:
            # A non mutable tuple should be fine as default argument, and it
            # has worked fine for years, but I do not trust it.  So we use None
            # as default.
            attendees = ()
        context = aq_inner(self.context)
        logger.info("Starting the EmailNotify.email() method with %r "
                    "attendees.", len(attendees))
        portal = getToolByName(context, 'portal_url').getPortalObject()
        plone_utils = getToolByName(portal, 'plone_utils')
        charset = plone_utils.getSiteEncoding()

        portal_props = getToolByName(self.context, 'portal_properties')
        mina_props = portal_props.get('minaraad_properties')
        fromAddress = mina_props.newsletter_from

        subject = '[%s] %s' % (portal.title_or_id(), renderer.context.Title())

        mailHost = getToolByName(portal, 'MailHost')

        failed_postings = []

        for attendee in attendees:
            emailBody = renderer.render(attendee)
            toAddress = attendee.email
            message = MIMEMultipart('alternative')
            html = emailBody['text/html']
            if isinstance(html, unicode):
                html = html.encode(charset)
            plain = emailBody['text/plain']
            if isinstance(plain, unicode):
                plain = plain.encode(charset)
            message.attach(MIMEText(plain, 'plain', charset))
            message.attach(MIMEText(html, 'html', charset))
            message = str(message)

            # Pick up some info to put in the logs in case of an
            # exception.
            send_info = DictLike(
                path=renderer.context.absolute_url(),
                message=emailBody,
                subject=subject,
                fromAddress=fromAddress,
                attendee=attendee,
                toAddress=toAddress,
            )

            try:
                logger.info("Starting mail to %s.", toAddress)
                mailHost.send(message,
                              mto=toAddress,
                              mfrom=fromAddress,
                              subject=subject)
            except Exception as exc:
                send_info.excname = str(exc.__class__.__name__)
                send_info.exctxt = str(exc)
                logger.error('Template %(path)s email failed sending from '
                             '%(fromAddress)s to %(toAddress)s '
                             '(%(excname)s: %(exctxt)s)',
                             send_info.__dict__)
                failed_postings.append(send_info)
            else:
                logger.info('Template %(path)s email succesfully sent '
                            'from %(fromAddress)s to %(toAddress)s',
                            send_info.__dict__)

        # Post a fake entry to error_log.
        # this enables to see failed postings from the ZMi, without the need
        # for an extra tool.
        # XXX Attention! Zope restart clears content of the error_log.
        # XXX increase "Number of exceptions to keep" from 20 to like 100
        if failed_postings:
            # post an entry to error_log (fake!)
            info = []
            info.append(
                ("Errors when sending out template %(path)s from "
                 "%(fromAddress)s" % failed_postings[0].__dict__))
            info.append('')
            info.append('To:\t\t\tException:'.expandtabs())
            for posting in failed_postings:
                info.append(
                    ('%(toAddress)s\t\t%(excname)s: %(exctxt)s' %
                     posting.__dict__).expandtabs())
            info.append('')
            info.append('%d errors in total' % len(failed_postings))
            # insert it
            error_log = getToolByName(context, 'error_log')
            error_log.raising(
                ['EmailSendError',
                 'This is not a real exception. See information below.',
                 '\n'.join(info)])
        # Return failures, a list of dictionaries with details on the emails.
        return failed_postings


class SubscriptionNotifyView(EmailNotify):

    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context, subscribe):
            super(SubscriptionNotifyView.EmailRenderer, self).__init__(context)
            self.subscribe = subscribe
            self.template = context.emailtemplate_subscribe_notification

        def render(self, attendee):
            template = self.template
            rendered = self.renderFromTemplate(template, attendee=attendee,
                                               subscribe=self.subscribe)
            return rendered

    def __call__(self, attendee, subscribe):
        context = aq_inner(self.context)
        attendees = [attendee]

        renderer = self.EmailRenderer(context, subscribe)
        failed_postings = self.email(renderer, attendees)

        return failed_postings
