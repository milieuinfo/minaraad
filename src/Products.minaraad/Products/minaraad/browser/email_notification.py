import transaction

from DateTime import DateTime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from textwrap import dedent

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from Products.minaraad.browser.configlets import AbstractView
from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.subscriptions import THEME_FILTERED
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

    def render(self, member):
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

    def email(self, renderer, members=()):
        """Email to members, using renderer.
        """
        context = aq_inner(self.context)
        logger.info("Starting the EmailNotify.email() method with %r members.",
                    len(members))
        portal = getToolByName(context, 'portal_url').getPortalObject()
        plone_utils = getToolByName(portal, 'plone_utils')
        charset = plone_utils.getSiteEncoding()

        portal_props = getToolByName(self.context, 'portal_properties')
        mina_props = portal_props.get('minaraad_properties')
        fromAddress = mina_props.newsletter_from

        subject = '[%s] %s' % (portal.title_or_id(), renderer.context.Title())

        mailHost = getToolByName(portal, 'MailHost')

        failed_postings = []

        for member in members:
            emailBody = renderer.render(member)
            toAddress = member.getProperty('email', '')
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
                member=member,
                toAddress=toAddress or 'N/A (%s)' % member.getProperty('id'),
                )

            try:
                logger.info("Starting mail to %s.", toAddress)
                mailHost.send(message,
                              mto=toAddress,
                              mfrom=fromAddress,
                              subject=subject)
            except Exception, exc:
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
        # return failed members
        return failed_postings


class EmailOutView(AbstractView, EmailNotify):

    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context, template):
            super(EmailOutView.EmailRenderer, self).__init__(context)
            self.text = context.REQUEST.get('additional', None)
            if self.text:
                plone_utils = getToolByName(context, 'plone_utils')
                charset = plone_utils.getSiteEncoding()
                self.text = safe_unicode(self.text, charset)
            self.template = template

        def render(self, member):
            rendered = self.renderFromTemplate(self.template, member=member)
            if self.text:
                rendered += self.renderFromText(self.text)
            return rendered

    def can_reset(self):
        """Can the user reset the emailSent time?

        This is only possible if the email has not been sent within a
        certain time, be default half an hour.
        """
        context = aq_inner(self.context)
        return not context.has_already_been_sent(limit_minutes=LIMIT_MINUTES)

    def sendEmail(self):
        logger.info("Start of EmailOutView.sendEmail.")
        context = aq_inner(self.context)
        request = self.request
        response = request.response

        if not request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            logger.debug("This is a GET request, so we should not send email.")
            return

        if request.get('send', None) is not None:
            logger.info("Yes, we should send email.")

            try:
                context.setEmail_themes(request.form.get('email_themes', []))
            except AttributeError:
                pass

            additionalMembers = [mem.strip() for mem in
                                 self.request.get('to', '').split(',')
                                 if mem]
            testing = bool(int(self.request.get('send_as_test', "0")))

            tool = getToolByName(context, 'portal_membership')
            members = [tool.getMemberById(memberid)
                       for memberid in additionalMembers]
            logger.info("We have %r members (just the 'additionalMembers').",
                        len(members))

            if not testing:
                logger.info("We are not in test mode.")
                sm = SubscriptionManager(context)
                themes = None
                if self.getSubscriptionId() in THEME_FILTERED:
                    themes = context.get_all_themes()
                    logger.info("We're filtering on theme: %s", themes)

                members = [
                    member for member in
                    sm.emailSubscribers(self.getSubscriptionId(), themes=themes)
                    ] + members
                logger.info(
                    ("Now we have %r members ('additionalMembers' "
                     "plus subscribers)." % len(members)))

                # We set the time that the email has been sent and
                # immediately commit the transaction.  This should
                # avoid sending the same emails twice.  First we check
                # if an email has already been sent.  If it has been
                # sent, and the user really wants to send it twice, he
                # must first explicitly reset the emailSent time.  See
                # the ResetEmailSent browser view.
                context.fail_if_already_sent()
                context.setEmailSent(DateTime())
                transaction.commit()
            else:
                logger.info("We are in test mode.")

            template = getattr(context, self.getTemplateName(), None)
            if template is None:
                template = getattr(context, "EmailTemplate-Default", None)

            renderer = self.EmailRenderer(context, template)

            failed_postings = self.email(renderer, members)
            logger.info("All the emails ought to be send now.")
            if failed_postings:
                failed = ', '.join([p.toAddress for p in failed_postings])
                message = (
                    "E-Mail versturen is mislukt naar de volgende addressen: "
                    "%s" % failed)
            else:
                message = 'E-mail is verstuurd.'
            logger.info("The referring url is %r.",
                        self.referring_url)
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)
        else:
            logger.debug("No, we should not send email; the template "
                         "is simply being shown, no form has been submitted.")

    def __call__(self):
        return self.index(template_id='email_out')

    def defaultTo(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return str(member)

    def canSend(self):
        # return self.context.getEmailSent() is None
        return True

    def sentDate(self):
        context = aq_inner(self.context)
        localize = context.restrictedTraverse('@@plone').toLocalizedTime
        return localize(time=context.getEmailSent(),
                        long_format=True)

    def getTemplateName(self):
        context = aq_inner(self.context)
        return "EmailTemplate-%s" % context.getPortalTypeName()

    def getSubscriptionId(self):
        """
        Returns the subscription id.  By default, this implementation
        will derive the subscription id from the class name.
        """
        context = aq_inner(self.context)
        name = context.__class__.__name__
        return name

    def show_theme_warning(self):
        """A theme field was added to two contenttypes, warn if it is None."""
        context = aq_inner(self.context)
        if context.__class__.__name__ in ['Study', 'Advisory']:
            if context.getTheme() is None:
                return True
        # In all other cases, no warning is needed.
        return False


class SubscriptionNotifyView(EmailNotify):

    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context, subscribe):
            super(SubscriptionNotifyView.EmailRenderer, self).__init__(context)
            self.subscribe = subscribe
            self.template = context.emailtemplate_subscribe_notification

        def render(self, member):
            template = self.template
            rendered = self.renderFromTemplate(template, member=member,
                                               subscribe=self.subscribe)
            return rendered

    def __call__(self, member, subscribe):
        context = aq_inner(self.context)
        members = [member]

        renderer = self.EmailRenderer(context, subscribe)
        failed_postings = self.email(renderer, members)

        return failed_postings


class EmailTestView(EmailNotify):

    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context):
            super(EmailTestView.EmailRenderer, self).__init__(context)
            self.template = context.emailtemplate_confirm_membership

        def render(self, member):
            template = self.template
            rendered = self.renderFromTemplate(template, member=member)
            return rendered

    def __call__(self):
        context = aq_inner(self.context)
        request = self.request

        tool = getToolByName(context, 'portal_url')
        portal = tool.getPortalObject()

        memberid = request.get('memberid')
        if memberid is not None:
            member = portal.portal_membership.getMemberById(memberid)
            if member is None:
                return "Gebruiker %s bestaat niet." % memberid
            members = [member]
        else:
            members = portal.portal_membership.listMembers()
        valid_members = [m for m in members if m.getProperty('email') and
                         '@' in m.getProperty('email')]
        renderer = self.EmailRenderer(context)
        failed_postings = self.email(renderer, valid_members)

        return u"Failed postings, if any: %r" % failed_postings


class ResetEmailSent(BrowserView):

    def __call__(self):
        if not self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            return "Error: only POST allowed."
        context = aq_inner(self.context)
        if context.has_already_been_sent(limit_minutes=LIMIT_MINUTES):
            return ("Error: the time limit has for resetting has not been "
                    "reached yet.")
        context.setEmailSent(None)
        return self.request.RESPONSE.redirect(
            context.absolute_url() + '/email_out')
