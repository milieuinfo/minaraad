from Products.Five import BrowserView
from urlparse import urljoin
from urlparse import urlparse


class RedirectPlone(BrowserView):
    """Redirect to the same view on a Plone Site instead of the Zope root.

    Problem:

    1. When you view www.minaraad.be and there is a link to
    /@@newsletter, say in the Diazo theme, you correctly end up at
    www.minaraad.be/@@newsletter.

    2. When you view localhost:8080/minaraad and there is that same link
    to /@@newsletter, you incorrectly end up at
    localhost:8080/@@newsletter.  That page usually does not exist and
    you wanted to go to localhost:8080/minaraad/@@newsletter instead.

    The RedirectPlone browser view solves this problem for selected
    views.

    Just register a browser page for the Zope Application root with the
    name you need.  For example:

      <browser:page
        name="newsletter"
        for="OFS.interfaces.IApplication"
        class=".helpers.RedirectPlone"
        permission="zope2.View"
        />

    There must be a referer.  Without referer we could look for any
    Plone Site in the Zope root, but let's not.  That is not the goal we
    are after.  Maybe later.
    """

    def __call__(self):
        # We want the Plone Site from the referer.
        referer = self.request['HTTP_REFERER']
        if not referer:
            return u'No referer found.'
        referer_info = urlparse(referer)
        own_info = urlparse(self.request.URL)
        if (referer_info.scheme != own_info.scheme or
                referer_info.netloc != own_info.netloc):
            return u'Referer is from different domain.'
        if '/' not in referer_info.path:
            return u'Missing slash in referer path.'
        plone_id = referer_info.path.split('/')[1]
        if plone_id not in self.context:
            return u'Path {} not in Zope root.'.format(plone_id)
        plone_site = getattr(self.context, plone_id)
        if getattr(plone_site, 'portal_type', '') != 'Plone Site':
            return u'Path {} is not a Plone Site.'.format(plone_id)
        # Use the original url as base and insert the plone id in the path.
        new_url = urljoin(self.request.URL, plone_id + own_info.path)
        if self.request['QUERY_STRING']:
            new_url += '?' + self.request['QUERY_STRING']
        return self.request.response.redirect(new_url)
