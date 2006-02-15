from Products.CMFCore.utils import getToolByName
from themes import ThemeManager

SUBSCRIPTIONS_ALL = ('Advisory', 'Study', 'Newsletter', 
                     'Pressrelease', 'AnnualReport')
SUBSCRIPTIONS_POST = ('Advisory', 'Study', 'AnnualReport')

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
        

    def _getSubscriptions(self):
        tool = getToolByName(self.portal, 'portal_membership')
        member = tool.getAuthenticatedMember()
        
        prop = member.getProperty('subscriptions', [])

        themeManager = ThemeManager(self.portal)
        themeItems = [Subscription('theme_'+str(id)) 
                      for id,title in themeManager.themes]

        subscriptions = [Subscription(x)
                         for x in SUBSCRIPTIONS_ALL] + themeItems

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
        return id in SUBSCRIPTIONS_ALL
    
    def canSubscribePost(self, id):
        return id in SUBSCRIPTIONS_POST
        

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
