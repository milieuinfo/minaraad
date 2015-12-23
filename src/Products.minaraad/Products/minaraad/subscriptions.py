
import logging

from Products.CMFCore.utils import getToolByName

from Products.minaraad.utils import list_match

logger = logging.getLogger('minaraad_email')


SUBSCRIPTIONS_EMAIL = ('AnnualReport',
                       'Study',
                       'NewsLetter',
                       'Pressrelease',
                       'Hearing',
                       'Advisory',
                       'MREvent')

THEME_FILTERED = ['Advisory',
                  'Hearing',
                  'Study']


class NotSubscribableError(Exception):

    def __init__(self, id, reason='No such subscription'):
        self.__init__("%s: %s" % (id, reason))
        self.id = id
        self.reason = reason


class SubscriptionManager(object):
    """Handles subscribing and subscription lists.

    Note that it is used as an adapter, but it isn't hooked up that way.
    """

    def __init__(self, portal):
        self.portal = portal

    def subscribe(self, id, email=True):
        subscriptions = self.subscriptions
        for subscription in subscriptions:
            if subscription.id == id:
                subscription.email = email
                self.subscriptions = subscriptions
                return

        raise NotSubscribableError(id)

    def getSubscriptionsForMemberId(self, memberid):
        tool = getToolByName(self.portal, 'portal_membership')
        member = tool.getMemberById(memberid)
        if member is None:
            return []
        return self._getSubscriptions(member)

    def getThemesForMemberId(self, memberid):
        tool = getToolByName(self.portal, 'portal_membership')
        member = tool.getMemberById(memberid)
        if member is None:
            return []
        return self._getThemes(member)

    def _getThemes(self, member=None):
        tool = getToolByName(self.portal, 'portal_membership')
        if member is None:
            member = tool.getAuthenticatedMember()
        #themeManager = ThemeManager(self.portal)
        #themeIds = [id for id, title in themeManager.themes]
        ourThemeIds = member.getProperty('themes', [])
        return ourThemeIds

    def _setThemes(self, themes, member=None):
        tool = getToolByName(self.portal, 'portal_membership')
        if member is None:
            member = tool.getAuthenticatedMember()
        lines = [str(x) for x in themes]
        member.setMemberProperties({'themes': lines})

    themes = property(_getThemes, _setThemes)

    def _getSubscriptions(self, member=None):
        tool = getToolByName(self.portal, 'portal_membership')
        if member is None:
            member = tool.getAuthenticatedMember()

        # Combine them, filtering out duplicates by using a set.
        allNames = SUBSCRIPTIONS_EMAIL
        # Just for testing/debugging: sort them.
        allNames = list(allNames)
        allNames.sort()

        subscriptions = [Subscription(x) for x in allNames]

        subDict = {}

        prop = member.getProperty('subscriptions', [])
        for line in prop:
            try:
                id, email, post = line.split('/')
                subDict[id] = {'subscribed_email': bool(int(email)),
                               'subscribed_post': bool(int(post))}
            except ValueError:
                # We have a new-style subscription with two entries.
                id, email = line.split('/')
                subDict[id] = {'subscribed_email': bool(int(email)),
                               'subscribed_post': False}

        for subscription in subscriptions:
            existing = subDict.get(subscription.id, None)
            if existing:
                subscription.email = existing['subscribed_email']

        return subscriptions

    def _setSubscriptions(self, subscriptions, member=None):
        tool = getToolByName(self.portal, 'portal_membership')
        if member is None:
            member = tool.getAuthenticatedMember()

        lines = ['%s/%i' % (x.id, x.email) for x in subscriptions]

        member.setMemberProperties({'subscriptions': tuple(lines)})

    subscriptions = property(_getSubscriptions, _setSubscriptions)

    def canSubscribeEmail(self, id):
        return id in SUBSCRIPTIONS_EMAIL

    def isEmailSubscribed(self, id):
        for x in self.subscriptions:
            if x.id == id:
                if x.email:
                    return True
                break

        return False

    def _subscribers(self, contenttype, type_, themes=None):
        logger.info('Gathering subscribers of type %r for %r.', type_,
                    contenttype)
        tool = getToolByName(self.portal, 'portal_membership')
        members = tool.listMembers()
        logger.info("portal_membership has %r members in total.",
                    len(members))

        subscribers = []
        if themes is None:
            themes = []

        for member in members:
            subscriptions = self._getSubscriptions(member)
            if contenttype in THEME_FILTERED:
                member_themes = self._getThemes(member)
                if not list_match(themes, member_themes):
                    logger.debug('Not selecting %r as there is no match between %r and %r',
                                 member, themes, member_themes)
                    continue
            for x in subscriptions:
                if x.id == contenttype:
                    if getattr(x, type_, False):
                        subscribers.append(member)
                    continue
        logger.info("%r out of them are subscribed.", len(subscribers))
        return subscribers

    def emailSubscribers(self, contenttype, themes=None):
        return self._subscribers(contenttype, 'email', themes=themes)


class Subscription(object):

    def __init__(self, id, email=False):
        self.id = id
        self.email = email

    def __repr__(self):
        return "<Subscription: id=%s; %s>" % (self.id, self.email)
    __str__ = __repr__
