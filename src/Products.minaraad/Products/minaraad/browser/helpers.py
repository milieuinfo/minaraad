from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from urlparse import urljoin
from urlparse import urlparse

class HelpersView(BrowserView):
    """ Various helpers to render links to the Documenten section.
    """

    def years(self):
        """ Return a dict of years and url's to the documenten section
            for the current theme and content type.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        ctype = self.context.portal_type
        theme = self.context.getThemeObject()

        # Sometimes objects are created with a effective date of
        # '1000-01-01 00:00:00'. Resulting in 1000+ values.
        # Therefore we limit `fist` to a reasonable effective date.
        first = catalog.searchResults(
                portal_type=ctype,
                sort_on='effective',
                sort_order='ascending',
                sort_limit=1,
                effective={
                    'query': (
                        DateTime('1980-01-01 00:00:00'),
                    ),
                    'range': 'min',
                }
        )[0].effective.year()
        last = catalog.searchResults(
                sort_on='effective',
                sort_order='descending',
                sort_limit=1
        )[0].effective.year()

        years = range(first, last, 1)
        years.reverse()
        portal_url = getToolByName(self.context, 'portal_url')()
        base_url = portal_url + '/documenten/'
        for yr in years:
            results.append({'year': yr,
               'url': base_url + '#c2='+ctype+'&c5='+str(yr) +'&c7=%2Fminaraad%2Fthemas%2F' + theme.getId()})

        return results

    def nextprev(self):
        """ Return links to the previous or next item. Depending on the location it will
            vary based on the context.

            - Items are ordered by effective date.
            - Only display items within the same theme.
            - Only display items with the same type.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        ctype = self.context.portal_type
        path = '/'.join(self.context.getThemeObject().getPhysicalPath())
        items = catalog.searchResults(portal_type=ctype,
                                      path=path,
                                      sort_on='effective',
                                      sort_order='ascending')
        pos = 0
        prev = None
        nxt = None
        for item in items:
            if item.getObject() == self.context:
                prev = pos - 1 if pos > 1 else None
                this = pos
                nxt = pos + 1
            pos += 1
        pos -= 1
        prev_dict = None
        if prev is not None and prev >= 0:
            prev_dict = dict(title=items[prev].Title,
                             url=items[prev].getURL())
        next_dict = None
        if nxt is not None and nxt <= pos:
            next_dict = dict(title=items[nxt].Title,
                             url=items[nxt].getURL())

        return {'next': next_dict, 'previous': prev_dict}


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

    Or several pages at once:

      <browser:pages
          for="OFS.interfaces.IApplication"
          class=".helpers.RedirectPlone"
          permission="zope2.View">
        <browser:page name="newsletter" />
        <browser:page name="login_form" />
        <browser:page name="logout" />
      </browser:pages>

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
