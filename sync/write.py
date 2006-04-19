from zope import interface
from zope import component

import urllib2
import time
from DateTime import DateTime

from CipraSync.interfaces import IPathResolver, IWriteHandler
from CipraSync.writehandler import BaseHandler, BasicHandler

from minaraad.sync.interfaces import IDontWrite

class MinaResolver:
    """Resolver for all mina types.

    Given a record with a category, this will found out where it
    belongs.  Currently only supports memberdata and returns the site
    root.

    >>> resolve = MinaResolver('/foo-raad').resolve
    >>> class Record(dict):
    ...     pass
    >>> r = Record()
    >>> r.category = 'mina-members'
    >>> resolve(r)
    '/foo-raad'

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

    Then there's the categories 'Advisory', 'File', and
    'Pressrelease':

    >>> r = Record()
    >>> r['date'] = (3535,)
    >>> for category in ('Advisory', 'File', 'Pressrelease'):
    ...     r.category = category
    ...     resolve(r)
    '/foo-raad/adviezen/adv_3535/'
    '/foo-raad/nieuwsbrieven/newsl_3535/'
    '/foo-raad/persberichten/pressr_3535/'
    """
    interface.implements(IPathResolver)

    scrapeCategories = {
        'Advisory': '/adviezen/adv_%s/',
        'File': '/nieuwsbrieven/newsl_%s/',
        'Pressrelease': '/persberichten/pressr_%s/',
        }

    def __init__(self, siteroot):
        self.siteroot = siteroot

    def resolve(self, record):
        if record.category == 'mina-members':
            return self.siteroot

        elif record.category in self.scrapeCategories.keys():
            path = self.scrapeCategories[record.category]
            return self.siteroot + (path % record['date'][0])
            
        raise ValueError("Unable to find a path for '%s'." % record)


class MemberPropertyHandler(BaseHandler):
    """An IWriteHandler that stores memberdata and creates members if
    necessary.

    Be warned that this doctest uses your actual Data.fs!  (You need a
    Plone Site called /minaraad for this test to work.)

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
    ...         return ('/minaraad')

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
    Customization policy for minaraad installed
    >>> app # doctest: +ELLIPSIS
    <Application at ...>

    Note that there's already a Plone site in our database:

    >>> plone = app.restrictedTraverse(Resolver().resolve(None))
    >>> plone
    <PloneSite at /minaraad>

    >>> plone.portal_membership.listMembers()
    []

    >>> writer.write()
    >>> members = plone.portal_membership.listMembers()
    >>> members
    [<MemberData at /minaraad/portal_memberdata/ahmad.ahadi used for /minaraad/acl_users>, <MemberData at /minaraad/portal_memberdata/john.doe used for /minaraad/acl_users>]
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


class ScrapeHandler(BasicHandler):
    """A write handler for the scrape transforms."""

    def write(self, record):
        path = self.resolver.resolve(record)
        portalType = record.category
        parent = self._getContainer(path)

        suitableId = self._suitableId(parent, record)
        parent.invokeFactory(portalType, suitableId)
        obj = getattr(parent, suitableId)

        self._update(obj, record)
        obj.reindexObject()

        get_transaction().commit(1)

    def _suitableId(self, parent, record):
        normalize = parent.plone_utils.normalizeString
        suitableId = normalize(record['title'])
        while suitableId in parent.objectIds():
            suitableId += '-2'
        return suitableId

    def _update(self, obj, record):
        obj.setTitle(record['title'])
        self.logger.debug("%s: Updated title." %
                          ('/'.join(obj.getPhysicalPath())))


class NieuwsbriefScrapeHandler(ScrapeHandler):
    def _suitableId(self, parent, record):
        normalize = parent.plone_utils.normalizeString
        name = normalize(record['files'][0].split('/')[-1])
        while name in parent.objectIds():
            name = 'copy_' + name
        return name
    
    def _update(self, obj, record):
        super(NieuwsbriefScrapeHandler, self)._update(obj, record)
        obj.setEffectiveDate(time.mktime(record['date']))


class FileScrapeHandler(ScrapeHandler):
    """This handles attachements."""
    def _update(self, obj, record):
        super(FileScrapeHandler, self)._update(obj, record)
        normalize = obj.plone_utils.normalizeString

        files = record['files']
        for url in files:
            name = normalize(url.split('/')[-1])
            while name in obj.objectIds():
                name = 'copy_' + name
            contents = urllib2.urlopen(url).read()
            obj.invokeFactory('File', name)
            fileObj = getattr(obj, name)
            fileObj.setFile(contents, mimetype='application/pdf')

        self.logger.debug("%s: Added %s files." %
                          ('/'.join(obj.getPhysicalPath()), len(files)))


class AdviezenScrapeHandler(FileScrapeHandler):
    def _update(self, obj, record):
        super(AdviezenScrapeHandler, self)._update(obj, record)

        persons = self._getContactPersons(obj, record['emails'])
        obj.setContact(persons)
        obj.setDate(time.mktime(record['date']))

    def _getContactPersons(self, context, emails):
        return [] # XXX


class PersberichtenScrapeHandler(FileScrapeHandler):
    def _update(self, obj, record):
        super(PersberichtenScrapeHandler, self)._update(obj, record)
        obj.setDate(time.mktime(record['date']))
