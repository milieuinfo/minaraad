from Products.minaraad.config import *
from StringIO import StringIO
from Globals import package_home
from Products.CMFCore.utils import getToolByName

out = StringIO()

# Because of a difference in Newsletter and NewsLetter we need to fix
# All member's subscriptions to the uppercase L

def fix(self):
    fixed_members = []
    members = getToolByName(self, 'portal_membership').listMembers()
    for member in members:
        subscriptions = member.getProperty('subscriptions',None)
        idx = 0
        for sub in subscriptions:
            if sub.startswith('Newsletter'):
                fixed_sub = sub.replace('Newsletter','NewsLetter')
                subscriptions[idx] = fixed_sub
                member.setProperties({'subscriptions':subscriptions})
                fixed_members.append(member.getId())
            idx += 1
    return fixed_members
    

