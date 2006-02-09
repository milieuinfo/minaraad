from sets import Set
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

def install(self):
    out = StringIO()

    out.write("Add member data properties.")
    addMemberDataProperties(self, out)

    return out.getvalue()


def addMemberDataProperties(self, out):
    """Added extra Memberdata information to the memberdata tool
    """
    memberdata = getToolByName(self, 'portal_memberdata')
    
    add_properties = Set(
        ('company', 'jobtitle', 'street', 'housenumber', 
         'zipcode', 'city', 'phonenumber',))
    add_properties -= Set(memberdata.propertyIds())
    for p in add_properties:
        memberdata.manage_addProperty(p, '', 'string')
        print >> out, "Property %r added to memberdata." % p

    # special care for our selection property gender
    if 'genders' not in memberdata.propertyIds():
        memberdata.manage_addProperty('genders', ['Heer','Mevrouw'], 'lines')

    if 'gender' not in memberdata.propertyIds():
        memberdata.manage_addProperty('gender', 'genders', 'selection')
    
    # adding Country
    countries = ['Belgie', 'Nederland', 'Ander land']
    
    if 'country' not in memberdata.propertyIds():
        memberdata.manage_addProperty('select_country', countries, 'lines')
        memberdata.manage_addProperty('country', 'select_country', 'selection')
        memberdata.manage_addProperty('other_country', '', 'string')
