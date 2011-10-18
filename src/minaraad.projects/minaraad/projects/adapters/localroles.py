from borg.localrole.interfaces import ILocalRoleProvider
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.utils import getToolByName

from minaraad.projects.interfaces import IProject, IMeeting


class LocalRoleProvider(object):
    implements(ILocalRoleProvider)
    role = 'ProjectMember'

    def __init__(self, context):
        self.context = context

    def get_member_by_id(self, m_id):
        """ Return the member object based on its id.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getMemberById(m_id)

    def get_group_by_id(self, g_id):
        """ Return the group object based on its id.
        """
        pgroups = getToolByName(self.context, 'portal_groups')
        return pgroups.getGroupById(g_id)

    def group_in_project(self, g_id, project=None):
        """ Ensures that a group works on a project.
        """
        if project is None:
            project = self.context

        return g_id == project.getResponsible_group() or \
               g_id in project.getAssigned_groups()

    def check_state(self, project=None):
        """ When projects are not activated, we do
        not do anything.
        """
        if project is None:
            project = self.context

        workflow = getToolByName(self.context, 'portal_workflow')
        state = workflow.getInfoFor(project, 'review_state')
        return state in ['active', 'finished', 'completed']


class ProjectLocalRoleProvider(LocalRoleProvider):
    adapts(IProject, )

    def getRoles(self, user_id):
        """
        """
        if not self.check_state():
            return ()

        user = self.get_member_by_id(user_id)
        if user is None:
            return ()

        for group_id in user.getGroups():
            if self.group_in_project(group_id):
                return (self.role, )

        return ()

    def getAllRoles(self):
        """
        """
        if not self.check_state():
            return

        gtool = getToolByName(self.context, 'portal_groups')
        for group_id in gtool.getGroupIds():
            if self.group_in_project(group_id):
                yield(group_id, (self.role, ))


class MeetingLocalRoleProvider(LocalRoleProvider):
    adapts(IMeeting, )

    def getRoles(self, user_id):
        user = self.get_member_by_id(user_id)
        if user is None:
            return ()

        for group_id in user.getGroups():
            if group_id in self.context.getInvited_groups():
                return (self.role, )

            for project in self.context.get_all_projects():
                if not self.check_state(project):
                    continue

                if self.group_in_project(group_id, project):
                    return (self.role, )
        return ()

    def getAllRoles(self):
        gtool = getToolByName(self.context, 'portal_groups')
        all_groups = list(self.context.getInvited_groups()) + \
                     [self.context.getResponsible_group()]

        for group_id in gtool.getGroupIds():
            if group_id in all_groups:
                yield (group_id, (self.role, ))
                break

            for project in self.context.get_all_projects():
                if self.group_in_project(group_id, project):
                    yield(group_id, (self.role, ))
                    break
