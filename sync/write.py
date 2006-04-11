from zope import interface
from zope import component

from CipraSync.interfaces import IPathResolver, IWriteHandler
from CipraSync.writehandler import BaseHandler

from minaraad.sync.interfaces import IDontWrite

SITEROOT = '/minaraad'

class MinaResolver:
    """Resolver for all mina types.

    Given a record with a category, this will found out where it
    belongs.  Currently only supports memberdata and returns the site
    root.

    >>> resolve = MinaResolver().resolve
    >>> class Record(dict):
    ...     pass
    >>> r = Record()
    >>> r.category = 'mina-members'
    >>> resolve(r)
    '/minaraad'

    >>> r = Record()
    >>> resolve(r) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: 'Record' object has no attribute 'category'
    >>> r.category = 'unknown'
    >>> resolve(r)
    Traceback (most recent call last):
    ...
    ValueError: Unable to find a path for '{}'.
    
    """
    interface.implements(IPathResolver)

    def resolve(self, record):
        if record.category == 'mina-members':
            return SITEROOT
        raise ValueError("Unable to find a path for '%s'." % record)


class MemberPropertyHandler(BaseHandler):
    """An IWriteHandler that stores memberdata and creates members if
    necessary.

    Be warned that this doctest uses your actual Data.fs!  (You need a
    Plone Site called /mina for this test to work.)

    An IRecord implementation:

    >>> from zope import interface
    >>> from CipraSync.interfaces import IRecord

    >>> class MyRecord(dict):
    ...     interface.implements(IRecord)
    ...     def __init__(self, category=None, **kwargs):
    ...         super(MyRecord, self).__init__(**kwargs)
    ...         self.category = category or ''

    (Writer will need the record.category for handler-lookup. Normally
    the schema name is provided in this value)
    
    A fake reader:

    >>> reader = [
    ...     MyRecord(fullname='Doe', firstname='John'),
    ...     MyRecord(fullname='Ahadi', firstname='Ahmad'),
    ... ]

    >>> for record in reader:
    ...     record.category = 'mina-members'

    A resolver:

    >>> from CipraSync.interfaces import IPathResolver

    >>> class Resolver:
    ...     interface.implements(IPathResolver)
    ...     def resolve(self, record):
    ...         return ('/mina')

    Register the resolver with the CA:

    >>> import zope.component
    >>> zope.component.provideUtility(Resolver(), name='mina-resolver')

    Let's register ourself as an IWriteHandler:

    >>> import CipraSync.writehandler
    >>> zope.component.provideAdapter(
    ...     MemberPropertyHandler,
    ...     name='mina-memberpropertyhandler')

    >>> from path import path
    >>> from CipraSync.write import Writer
    >>> config = path(__file__).parent / 'etc' / 'writer.ini'
    >>> writer = Writer(reader, config)

    Let's abuse '_getDatabase' so that we have our own pointer to
    the database:

    >>> app = writer._getDatabase()
    Customization policy for CompoundField installed
    Customizationpolicy for PloneSelenium installed
    Customization policy for minaraad installed
    >>> app # doctest: +ELLIPSIS
    <Application at ...>

    Note that there's already a Plone site in our database:

    >>> plone = app.restrictedTraverse(Resolver().resolve(None))
    >>> plone
    <PloneSite at /mina>

    >>> plone.portal_membership.listMembers()
    []

    >>> writer.write()
    >>> members = plone.portal_membership.listMembers()
    >>> members
    [<MemberData at /mina/portal_memberdata/ahmad.ahadi used for /mina/acl_users>, <MemberData at /mina/portal_memberdata/john.doe used for /mina/acl_users>]
    """

    def write(self, record):
        portal_path = self.resolver.resolve(record)
        portal = self.context.app.restrictedTraverse(portal_path)

        plone_utils = portal.plone_utils
        membership = portal.portal_membership

        props = {}
        for key, value in record.items():
            if not IDontWrite.providedBy(value):
                props[key] = plone_utils.utf8_portal(value)
        
        memberid = self._suitableId(props, portal)

        # A policy for updating members?
        if membership.getMemberById(memberid) is None:
            password = list(memberid)
            password.reverse()
            password = ''.join(password[:3])
            membership.addMember(id=memberid,
                                 password=password,
                                 roles=['Member'],
                                 domains=[])

        plone_utils.setMemberProperties(memberid, **props)

    def _suitableId(self, props, portal):
        # This should really be a transform, but since we need the
        # tool to do normalizeString, we'll just do it the dirty way.
        normalize = portal.plone_utils.normalizeString

        if props['fullname']:
            memberid = normalize(props['fullname'])
            if props['firstname']:
                memberid = '%s.%s' % (normalize(props['firstname']), memberid)

        elif props['company']: # we don't have a fullname, use company
            memberid = normalize(props['company'])

        else:
            raise ValueError("Couldn't find a suitable memberid for %s" %
                             props)

        return memberid.replace('-', '')

        

        
