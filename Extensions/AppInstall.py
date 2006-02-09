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
         'zipcode', 'city', 'country', 'phonenumber',))
    add_properties -= Set(memberdata.propertyIds())
    for p in add_properties:
        memberdata.manage_addProperty(p, '', 'string')
        print >> out, "Property %r added to memberdata." % p

    # special care for our selection property gender
    if 'genders' not in memberdata.propertyIds():
        memberdata.manage_addProperty('genders', ['Heer','Mevrouw'], 'lines')

    if 'gender' not in memberdata.propertyIds():
        memberdata.manage_addProperty('gender', 'genders', 'selection')
    
    # special care for our selection property content types
    content_types = ['AnnualReport', 'NewsLetter', 'Pressrelease',]
    
    if 'subscriptions' not in memberdata.propertyIds():
        memberdata.manage_addProperty('subscriptions', content_types, 'lines')

    if 'subscription' not in memberdata.propertyIds():
        memberdata.manage_addProperty('subscription', 'subscriptions', 'selection')
    
    # adding checkboxes for Study and Advisory. Subscribers can choose: email, post or both
    options_study = ['per e-mail', 'per post', 'beide']
    options_advisory = options_study
    
    if 'Study' not in memberdata.propertyIds():
        memberdata.manage_addProperty('Study', 0 , 'boolean')
        memberdata.manage_addProperty('post_study', options_study, 'lines')
        memberdata.manage_addProperty('option_study', 'post_study', 'selection')

    if 'Advisory' not in memberdata.propertyIds():
        memberdata.manage_addProperty('Advisory', 0 , 'boolean')
        memberdata.manage_addProperty('post_advisory', options_advisory, 'lines')
        memberdata.manage_addProperty('option_advisory', 'post_advisory', 'selection')

    # adding 'Hoorzitting' and it's theme   s
    # code need to be written
