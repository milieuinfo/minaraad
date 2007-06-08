from Products.CMFCore.utils import getToolByName
from themes import ThemeManager
import logging
logger = logging.getLogger('minaraad_email')


SUBSCRIPTIONS_EMAIL = ('AnnualReport', 'Study', 
                     'NewsLetter', 'Pressrelease')
SUBSCRIPTIONS_POST = ('Advisory', 'Study', 'AnnualReport')
THEME_PARENT = 'Hearing'

class NotSubscribableError(Exception):
    
    def __init__(self, id, reason='No such subscription'):
        self.__init__("%s: %s" % (id, reason))
        self.id = id
        self.reason = reason

class SubscriptionManager(object):
    
    def __init__(self, portal):
        self.portal = portal

    def subscribe(self, id, email=True, post=True):
        subscriptions = self.subscriptions
        for subscription in subscriptions:
            if subscription.id == id:
                subscription.email = email
                subscription.post = post
                self.subscriptions = subscriptions
                return
            
        raise NotSubscribableError(id)

    def _getSubscriptions(self, member=None):
        tool = getToolByName(self.portal, 'portal_membership')
        if member is None:
            member = tool.getAuthenticatedMember()
        
        prop = member.getProperty('subscriptions', [])

        themeManager = ThemeManager(self.portal)
        themeItems = [Subscription('theme_'+str(id)) 
                      for id,title in themeManager.themes]

        # Combine the lists of email and post subscribers
        allSubscriptionNames = [x for x in SUBSCRIPTIONS_EMAIL]
        for sub in SUBSCRIPTIONS_POST:
            if sub not in SUBSCRIPTIONS_EMAIL:
                allSubscriptionNames.append(sub)

        subscriptions = [Subscription(x)
                         for x in allSubscriptionNames] + themeItems

        subDict = {}
        
        for line in prop:
            id, email, post = line.split('/')
            subDict[id] = {'subscribed_email': bool(int(email)),
                           'subscribed_post': bool(int(post))}

        for subscription in subscriptions:
            existing = subDict.get(subscription.id, None)
            if existing:
                subscription.email = existing['subscribed_email']
                subscription.post = existing['subscribed_post']
        
        return subscriptions

    def _setSubscriptions(self, subscriptions):
        tool = getToolByName(self.portal, 'portal_membership')
        member = tool.getAuthenticatedMember()

        lines = ['%s/%i/%i' % (x.id, x.email, x.post)
                 for x in subscriptions]

        member.setProperties(subscriptions=lines)
        
    subscriptions = property(_getSubscriptions, _setSubscriptions)

    def canSubscribeEmail(self, id):
        return id in SUBSCRIPTIONS_EMAIL or id == THEME_PARENT
    
    def canSubscribePost(self, id):
        return id in SUBSCRIPTIONS_POST
    
    def isEmailSubscribed(self, id):
        for x in self.subscriptions:
            if x.id == id:
                if x.email:
                    return True
                break
        
        return False
        
    def isPostSubscribed(self, id):
        for x in self.subscriptions:
            if x.id == id:
                if x.post:
                    return True
                break
        
        return False

    def _subscribers(self, id, type_):
        logger.info('Gathering subscribers of type %r.', type_)
        tool = getToolByName(self.portal, 'portal_membership')
        members = tool.listMembers()
        log.info("portal_membership has %r members in total.",
                 len(members))
        
        subscribers = []
        for member in members:
            subscriptions = self._getSubscriptions(member)
            for x in subscriptions:
                if x.id == id:
                    if getattr(x, type_, False):
                        subscribers.append(member)
                    break
        log.info("%r out of them are subscribed.", len(subscribers))
        return subscribers
    
    def emailSubscribers(self, id):
        return self._subscribers(id, 'email')
        
    def postSubscribers(self, id):
        return self._subscribers(id, 'post')

class Subscription(object):

    def __init__(self, id, post=False, email=False):
        self.id = id
        self.post = post
        self.email = email

    def __repr__(self):
        return "<Subscription: id=%s; post=%s; email=%s>" % (self.id,
                                                             self.post,
                                                             self.email)
    __str__ = __repr__
