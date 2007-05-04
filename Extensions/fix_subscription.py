from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

out = StringIO()

# Because of a difference in Newsletter and NewsLetter we need to fix
# All member's subscriptions to the uppercase L

def fix(self):
    fixed_members = []
    members = getToolByName(self, 'portal_membership').listMembers()
    for member in members:
        subscriptions = member.getProperty('subscriptions', None)
        fixed_subs = []
        changed = False
        for sub in subscriptions:
            if sub.startswith('Newsletter'):
                fixed_sub = sub.replace('Newsletter', 'NewsLetter')
                changed = True
            else:
                fixed_sub = sub
            fixed_subs.append(fixed_sub)
        if changed:
            member.setMemberProperties(dict(subscriptions = tuple(fixed_subs)))
            fixed_members.append(member.getId())
    return 'Fixed: %i %s' % (len(fixed_members), fixed_members)
