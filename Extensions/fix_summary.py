from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

out = StringIO()

# First: do a schema update for study/advisory/hearing.
# Second: run this external method. It migrates study/advisory's description
# field's contents to the new body field (if empty).

def fix(self):
    bodycount = 0
    desccount = 0
    for brain in self.portal_catalog(portal_type=['Study', 'Advisory']):
        print >> out, '============================'
        print >> out, brain.getId
        obj = brain.getObject()
        desc = obj.Description().strip()
        body = obj.getBody().strip()
        if not body:
            print >> out, 'Empty body'
            bodycount += 1
            if desc:
                print >> out, 'But we do have a description'
                desccount += 1
                obj.setBody(desc)
                obj.setDescription('')
                print >> out, 'Description moved to body'


    print >> out, '======================================'
    print >> out, '======== Summary ====================='
    print >> out, '======================================'
    print >> out, 'Empty bodies: %s' % bodycount
    print >> out, 'Empty descriptions: %s' % desccount
    return out.getvalue()
