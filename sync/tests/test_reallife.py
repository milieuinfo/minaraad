import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctest import ELLIPSIS

from zope import component

from CipraSync import interfaces


import utils

def setUp(test):
    utils.setUpEnviron()

def tearDown(test):
    utils.tearDownEnviron()

class TestRealLife:
    """A test that actually reads in data from a source and writes
    data to a ZODB.

    >>> import glob
    >>> from path import path

    >>> import zope.component

    >>> from CipraSync import interfaces
    >>> import minaraad.sync.configure
    >>> 
    >>> minaraad.sync.configure.all()

    Let's try to import the members data:

    >>> reader = zope.component.getUtility(interfaces.IReader)
    >>> filenames = [path(__file__).parent.parent / 'input' /
    ...              'Nieuwbriefbestand.csv']
    >>> reader.feed(filenames)
    >>> writer = interfaces.IWriter(reader)
    >>> writer.write()
    Customization policy for minaraad installed
    >>> app = writer._getDatabase()
    >>> membership = app.mina.portal_membership
    >>> memberdata = membership.listMembers()
    >>> len(memberdata)
    2660

    Before we introspect some of our members, let's write a handy
    function that will help us display the member's data in a
    well-defined fashion:

    >>> def printmember(member):
    ...     props = member.__dict__
    ...     names = props.keys()
    ...     names.sort()
    ...     for name in names:
    ...         print '%s: %r' % (name, getattr(member, name))

    The last person in the alphabet:
    
    >>> printmember(memberdata[-1])
    bus: ''
    city: 'Mechelen'
    company: 'VMM'
    country: 'Belgie'
    email: ''
    firstname: 'Yvo'
    fullname: 'Porters'
    gender: 'De heer'
    housenumber: '34'
    id: 'yvo.porters'
    jobtitle: ''
    phonenumber: ''
    street: 'Van Benedenlaan'
    zipcode: '2800'

    There's company called VRWB...

    >>> printmember(membership.getMemberById('vrwb'))
    bus: ''
    city: 'Brussel'
    company: 'VRWB'
    country: 'Belgie'
    email: 'vrwb@vlaanderen.be'
    firstname: ''
    fullname: ''
    gender: ''
    housenumber: '7'
    id: 'vrwb'
    jobtitle: ''
    phonenumber: ''
    street: 'Koning Albert II-laan'
    zipcode: '1210'

    ... and a member with this id who lives in the Netherlands and has
    a phonenumber:

    >>> printmember(membership.getMemberById('nico.baken'))
    bus: ''
    city: 'Voorburg'
    company: 'KPN'
    country: 'Nederland'
    email: 'nico.baken@kpn.com'
    firstname: 'Nico'
    fullname: 'Baken'
    gender: 'De heer'
    housenumber: '187'
    id: 'nico.baken'
    jobtitle: ''
    phonenumber: '0031 70 343 91 37'
    street: 'Oosteinde'
    zipcode: '2271EE'
    """

def test_suite():
    return DocTestSuite(setUp=setUp, tearDown=tearDown, optionflags=ELLIPSIS)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')