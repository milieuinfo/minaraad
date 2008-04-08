from configlets import AbstractView
from Products.CMFCore.utils import getToolByName
import urllib
from Products.Five import BrowserView
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import os, logging
from textwrap import dedent
from Products.minaraad.subscriptions import SubscriptionManager
from DateTime import DateTime

# Arrange logging
logger = logging.getLogger('minaraad_email')
# Also log these messages to a separate file
# XXX this may be possible through zope.conf too but I can't figure out
logpath = '%(INSTANCE_HOME)s/log/minaraad_email.log' % os.environ
hdlr = logging.FileHandler(logpath)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

 
class DictLike(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def fixRelativeUrls(xml, portal_url):
    return xml.replace('./resolveUid', portal_url + '/resolveUid')


class RenderedContent(dict):

    def __init__(self, dict=None):
        if dict is None:
            dict = {'text/plain': '', 'text/html': ''}
        super(RenderedContent, self).__init__(dict)

    def __add__(self, other):
        self['text/plain'] += '\n%s' % (other['text/plain'], )
        self['text/html'] += other['text/html']
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
        cooked = email_template.pt_render(extra_context=kwargs)
        cooked = fixRelativeUrls(cooked, getToolByName(self.context, 'portal_url')())
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        
        body = RenderedContent({
            'text/html': cooked,
            'text/plain': portal_transforms('lynx_dump', cooked),
        })

        return body

    def renderFromText(self, text):
        """
        Return both plain and html versions (a dict with keys
        'text/plain' and 'text/html') of a given text.
        """
        body = RenderedContent({
            'text/plain': text,
            'text/html': dedent('''\
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

        logger.info("Starting the EmailNotify.email() method with %r members.",
                    len(members))
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        plone_utils = getToolByName(portal, 'plone_utils')
        charset = plone_utils.getSiteEncoding()
        
        fromAddress = portal.getProperty('email_from_address')
        
        subject = '[%s] %s' % (portal.title_or_id(), renderer.context.Title())
        
        mailHost = getToolByName(portal, 'MailHost')
        
        failed_postings = []

        for member in members:
            emailBody = renderer.render(member)
            toAddress = member.getProperty('email', '')
            message = MIMEMultipart('alternative')
            message.attach(MIMEText(emailBody['text/plain'], 'plain', charset))
            message.attach(MIMEText(emailBody['text/html'], 'html', charset))
            message = str(message)
        
            send_info = DictLike(
                path = renderer.context.absolute_url(),
                message = emailBody,   # XXX why emailBody?
                subject = subject,
                fromAddress = fromAddress,
                member = member,
                toAddress = toAddress or 'N/A (%s)' % member.getProperty('id'),
                )

            try:
                logger.info("Starting mail to %s.", toAddress)
                mailHost.send(message = message,
                              mto = toAddress,
                              mfrom = fromAddress,
                              subject = subject)
            except Exception, exc:
                # XXX traceback is not needed now
                #log_exc('Could not send email from %(fromAddress)s to %(toAddress)s regarding issue ' \
                #        'in tracker %(path)s\ntext is:\n%(message)s\n' % send_info.__dict__)
                send_info.excname = str(exc.__class__.__name__)
                send_info.exctxt = str(exc)
                logger.error('Template %(path)s email failed sending from '
                             '%(fromAddress)s to %(toAddress)s '
                             '(%(excname)s: %(exctxt)s)',
                             send_info.__dict__)
                failed_postings.append(send_info);
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
            info.append('Errors when sending out template %(path)s from %(fromAddress)s' % failed_postings[0].__dict__)
            info.append('')
            info.append('To:\t\t\tException:'.expandtabs())
            for posting in failed_postings:
                info.append(('%(toAddress)s\t\t%(excname)s: %(exctxt)s' % send_info.__dict__).expandtabs())
            info.append('')
            info.append('%d errors in total' % len(failed_postings))
            # insert it
            error_log = getToolByName(self.context, 'error_log')
            error_log.raising(['EmailSendError', 'This is not a real exception. See information below.', '\n'.join(info)])
        # return failed members
        return failed_postings


class EmailOutView(AbstractView, EmailNotify):
    
    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context, template):
            super(EmailOutView.EmailRenderer, self).__init__(context)
            self.text = context.request.get('additional', None)
            self.template = template

        def render(self, member):
            rendered = self.renderFromTemplate(self.template, member=member)
            if self.text:
                rendered += self.renderFromText(self.text)
            return rendered

    def sendEmail(self):
        logger.info("Start of EmailOutView.sendEmail.")
        request = self.request
        response = request.response
        
        if request.get('send', None) is not None:
            logger.info("Yes, we should send email.")
            additionalMembers = [mem.strip() for mem in
                                 self.request.get('to', '').split(',')
                                 if mem]
            testing = bool(int(self.request.get('send_as_test', "0")))
            
            tool = getToolByName(self.context, 'portal_membership')
            members = [tool.getMemberById(memberid)
                       for memberid in additionalMembers]
            logger.info("We have %r members (just the 'additionalMembers').",
                        len(members))
            if not testing:
                logger.info("We are not in test mode.")
                sm = SubscriptionManager(self.context)
                members = [member for member in
                           sm.emailSubscribers(self.getSubscriptionId())] + \
                           members
                logger.info("Now we have %r members ('additionalMembers' plus subscribers).",
                            len(members))
                self.context.setEmailSent(DateTime())
            else:
                logger.info("We are in test mode.")
  
            template = getattr(self.context, self.getTemplateName(), None)
            if template is None:
                template = getattr(self.context, "EmailTemplate-Default", None)

            renderer = self.EmailRenderer(self.context, template)

            failed_postings = self.email(renderer, members)
            logger.info("All the emails ought to be send now.")
            if failed_postings:
                message = "E-Mail failed to following addresses: %s" % (
                    ', '.join([send_info.toAddress for send_info in failed_postings]),
                    )
            else:
                message = 'E-mail Sent'
            logger.info("The referring url is %r.",
                        self.context.referring_url)
                    
            return response.redirect(
                '%s?portal_status_message=%s' % (
                self.context.referring_url,
                urllib.quote_plus(message)))
        else:
            logger.info("No, we should not send email; the template "
                        "is simply being shown, no form has been submitted.")

    def __call__(self):
        return self.context.index(template_id='email_out')

    def defaultTo(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return str(member)

    def canSend(self):
       # return self.context.getEmailSent() is None
       return True
    
    def sentDate(self):
        localize = self.context.toLocalizedTime
        return localize(time=self.context.getEmailSent(),
                        long_format=True)
      
    def getTemplateName(self):
        return "EmailTemplate-%s" % self.context.getPortalTypeName()

    def getSubscriptionId(self):
        """
        Returns the subscription id.  By default, this implementation
        will derive the subscription id from the class name.
        """
        name = self.context.__class__.__name__
        if name == 'Hearing':
            name = 'theme_%d' % self.context.getTheme()
        return name


class SubscriptionNotifyView(EmailNotify):
    
    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context, subscribe):
            super(SubscriptionNotifyView.EmailRenderer, self).__init__(context)
            self.subscribe = subscribe
            self.template = self.context.emailtemplate_subscribe_notification

        def render(self, member):
            template = self.template
            rendered = self.renderFromTemplate(template, member=member, subscribe=self.subscribe)
            return rendered

    def __call__(self, member, subscribe):
        request = self.request
        response = request.response
        members = [member]

        renderer = self.EmailRenderer(self.context, subscribe)
        failed_postings = self.email(renderer, members)

        return failed_postings


class EmailTestView(EmailNotify):

    class EmailRenderer(EmailNotify.EmailRenderer):

        def __init__(self, context):
            super(EmailTestView.EmailRenderer, self).__init__(context)
            self.template = self.context.emailtemplate_confirm_membership

        def render(self, member):
            template = self.template
            rendered = self.renderFromTemplate(template, member=member)
            return rendered

    def __call__(self):
        request = self.request
        response = request.response

        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()

        #members = [portal.portal_membership.getMemberById('zest')]
        members = portal.portal_membership.listMembers()
        valid_members = [m for m in members if m.getProperty('email') and
                                               '@' in m.getProperty('email') ]
        renderer = self.EmailRenderer(self.context)
        failed_postings = self.email(renderer, valid_members)

        return failed_postings
