import logging

from zope.testing import doctest
from Products.PloneTestCase import PloneTestCase as ptc
from Testing import ZopeTestCase as ztc
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase.layer import onsetup
from Products.Five.testbrowser import Browser
from AccessControl import SecurityManagement

from zope.component import getSiteManager
from Products.MailHost.interfaces import IMailHost
from Products.PasswordResetTool.tests.utils import MockMailHost as \
     _MockMailHost

from digibib_view_parser import DigiBibHtmlParser
from minaraad.projects.setuphandlers import add_catalog_indexes

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def login_as_portal_owner(app):
    uf = app.acl_users
    owner = uf.getUserById(ptc.portal_owner)
    if not hasattr(owner, 'aq_base'):
        owner = owner.__of__(uf)
    SecurityManagement.newSecurityManager(None, owner)
    return owner


def get_portal():
    app = ztc.app()
    login_as_portal_owner(app)
    return getattr(app, ptc.portal_name)


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    #import Products.minaraad
    #zcml.load_config('configure.zcml', Products.minaraad)
    import minaraad.projects
    zcml.load_config('configure.zcml', minaraad.projects)
    fiveconfigure.debug_mode = False
    #ztc.installProduct('minaraad')
    ztc.installPackage('minaraad.projects')
    add_catalog_indexes(get_portal())


setup_product()
ptc.setupPloneSite(products=['minaraad.projects'])


class MockMailHost(_MockMailHost):

    def send(self, message,
             mto=None, mfrom=None, subject=None, encode=None,
             *args, **kwargs):
        self.messages.append({'to': mto,
                              'title': subject,
                              'msg': message})

    secureSend = send


class MockLogger:
    def __init__(self, name):
        self.name = name

    def info(self, msg):
        print 'INFO LOG [%s] %s' % (self.name, msg)

    def error(self, msg):
        print 'ERROR LOG [%s] %s' % (self.name, msg)

    def debug(self, msg):
        print 'DEBUG LOG [%s] %s' % (self.name, msg)


class MockMinaraadProperties:
    secretary_email = 'secretary@example.com'
    governance_board = 'daily_governance'


class MinaraadTestCase(ptc.PloneTestCase):
    default_password = 'secret'

    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.patch_error_log()
        self.patch_mail_host()
        self.patch_portal_properties()
        #self.patch_logger()

    def patch_error_log(self):
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

    def patch_mail_host(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

    def patch_portal_properties(self):
        pprops = self.portal.portal_properties
        pprops.minaraad_properties = MockMinaraadProperties()

    def patch_logger(self):
        def fake_getLogger(name):
            return MockLogger(name)

        logging.old_getLogger = logging.getLogger
        logging.getLogger = fake_getLogger

    def add_digibib(self):
        self.portal.invokeFactory('DigiBib', id='digibib')
        self.portal.digibib.invokeFactory('ProjectContainer', id='projects')
        self.portal.digibib.invokeFactory('MeetingContainer', id='meetings')
        self.portal.digibib.invokeFactory('OrganisationContainer', id='organisations')

    def add_group(self, g_id):
        self.portal.portal_groups.addGroup(g_id)

    def add_user(self, u_id, groups, roles=None, password=None):
        if password is None:
            password = self.default_password

        if roles is None:
            roles = []

        roles.extend(['Member', 'Reader'])
        self.portal.portal_membership.addMember(
            u_id,
            password,
            [],
            [],
            {'email': '%s@example.com' % u_id})

        self.portal.manage_setLocalRoles(u_id, roles)

        pgroups = self.portal.portal_groups
        for group_id in groups:
            if not pgroups.searchGroups(id=group_id):
                continue

            group = pgroups.getGroupById(group_id)
            group.addMember(u_id)

    def add_project(self, p_id, title, responsible_grp, assigned_grps):
        self.portal.digibib.projects.invokeFactory(
            'Project',
            id=p_id,
            title=title,
            responsible_group=responsible_grp,
            assigned_groups=assigned_grps)

    def add_meeting(self, m_id, title, groups, projects, start_time):
        self.portal.digibib.meetings.invokeFactory(
            'Meeting',
            id=m_id,
            title=title,
            start_time=start_time,
            invited_groups=groups)
        wft = self.portal.portal_workflow
        wft.doActionFor(self.portal.digibib.meetings[m_id],
                        'plan')

        for p_id in projects:
            self.portal.digibib.meetings[m_id].invokeFactory(
                'AgendaItemProject',
                id='agenda_%s' % p_id,
                duration=10,
                project=self.portal.digibib.projects[p_id].UID())
            self.portal.digibib.meetings[m_id][
                'agenda_%s' % p_id].setDuration(10)
            self.portal.digibib.meetings[m_id][
                'agenda_%s' % p_id].reindexObject()

    def change_workflow(self,
                        p_id,
                        incorrect_states=[],
                        steps=[]):
        wft = self.portal.portal_workflow
        project = self.portal.digibib.projects[p_id]
        state = wft.getInfoFor(project, 'review_state')

        if state in incorrect_states:
            raise ValueError('Project is in an incorrect state: %s' % state)

        for st, action in steps:
            if state == st:
                if action == 'validate':
                    project.setAdvisory_type('unanimous')
                elif action == 'reject':
                    project.setAdvisory_type('abstention')

                try:
                    wft.doActionFor(project, action)
                except:
                    raise Exception('No transition called %s' % action)

                state = wft.getInfoFor(project, 'review_state')

    def check_project(self, p_id):
        self.change_workflow(
            p_id,
            ['in_consideration', 'rejected',
             'active', 'cancelled', 'finished', 'completed'],
            steps=[('new', 'check')])

    def propose_project(self, p_id):
        self.change_workflow(
            p_id,
            ['rejected', 'cancelled', 'finished', 'completed'],
            steps=[('new', 'check'),
                   ('in_verification', 'propose')])

    def reject_project(self, p_id):
        self.change_workflow(
            p_id,
            ['active', 'cancelled', 'finished', 'completed'],
            steps=[('new', 'check'),
                   ('in_verification', 'propose'),
                   ('in_consideration', 'reject')])

    def start_project(self, p_id):
        self.change_workflow(
            p_id,
            ['rejected', 'cancelled', 'completed', 'finished'],
            steps=[('new', 'check'),
                   ('in_verification', 'propose'),
                   ('in_consideration', 'start')])

    def cancel_project(self, p_id):
        self.change_workflow(
            p_id,
            ['rejected', 'completed', 'finished'],
            steps=[('new', 'check'),
                   ('in_verification', 'propose'),
                   ('in_consideration', 'start'),
                   ('active', 'cancel')])

    def roundup_project(self, p_id):
        self.change_workflow(
            p_id,
            ['rejected', 'cancelled', 'finished'],
            steps=[('new', 'check'),
                   ('in_verification', 'propose'),
                   ('in_consideration', 'start'),
                   ('active', 'roundup')])

    def complete_project(self, p_id):
        self.change_workflow(
            p_id,
            ['rejected', 'cancelled'],
            steps=[('new', 'check'),
                   ('in_verification', 'propose'),
                   ('in_consideration', 'validate'),
                   ('active', 'roundup'),
                   ('finished', 'complete')])


class MinaraadFunctionalTestCase(MinaraadTestCase, ptc.FunctionalTestCase):

    def check_shown_in_digibib(self, user_id, object_ids, container):
        browser = Browser()

        browser.open('%s/logout/' % self.portal.absolute_url())
        browser.open('%s/login_form/' % self.portal.absolute_url())
        browser.getControl(name='__ac_name').value = user_id
        browser.getControl(name='__ac_password').value = self.default_password
        browser.getControl(name='submit').click()

        browser.open(self.portal.digibib.absolute_url())

        parser = DigiBibHtmlParser()
        parser.feed(browser.contents)

        # We have to check that the project is displayed in the main
        # content of the page and not simply in the menu on the left.
        return [obj_id for obj_id in object_ids
                if container[obj_id].absolute_url()
                in parser.links]
