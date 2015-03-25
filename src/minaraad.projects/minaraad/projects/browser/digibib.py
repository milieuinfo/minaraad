from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


def project_sort_key(brain):
    adv_date = brain.getAdvisory_date
    if adv_date:
        year = adv_date.year()
    else:
        year = 0
    num = brain.getProject_number
    return (year, num)


class DigiBibView(BrowserView):
    """ Default view of a DigiBib.
    """

    @property
    def mtool(self):
        return getToolByName(self.context, 'portal_membership')

    @property
    def ctool(self):
        return getToolByName(self.context, 'portal_catalog')

    def _sort_meetings(self, m, brains=False, reverse=False):
        if brains:
            sort_key = lambda x: x.getStart_time
        else:
            sort_key = lambda x: x.getStart_time()
        return sorted(m, key=sort_key, reverse=reverse)

    def _sort_projects(self, p, reverse=False):
        return sorted(p, key=project_sort_key, reverse=reverse)

    def _filter_projects(self, brains):
        """Filter project brains.

        This basically does the same as adapters/localroles.py.  But
        now we do it for all projects in one go, without needing to
        get the objects to ask if we have a permission there.
        """
        if self.mtool.checkPermission(
                'minaraad.projects: view project in digibib', self.context):
            # The user already has the right permission in the digibib
            # context, so she can see all projects.  She probably has
            # the Manager or Council Member role.
            return brains

        filtered = []
        pps = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state")
        if pps.anonymous():
            return filtered
        member = pps.member()
        group_ids = member.getGroups()
        for brain in brains:
            state = brain.review_state
            if state not in ['active', 'finished', 'completed']:
                continue
            found = False
            for group_id in group_ids:
                if group_id == brain.getResponsible_group:
                    found = True
                    break
                if group_id in brain.getAssigned_groups:
                    found = True
                    break
            if not found:
                continue
            filtered.append(brain)
        return filtered

    def list_projects(self):
        project_brains = self.ctool(
            {'portal_type': 'Project',
             'review_state': ['in_consideration', 'active', 'finished']})
        filtered = self._filter_projects(project_brains)
        return self._sort_projects(filtered)

    def list_all_projects(self):
        project_brains = self.ctool({'portal_type': 'Project'})
        filtered = self._filter_projects(project_brains)
        return self._sort_projects(filtered)

    def list_meetings(self):
        try:
            meeting_container = self.context.meetings
        except AttributeError:
            # Fresh Digibib?
            return []
        # Note: these are now brains.
        meetings = meeting_container.list_meetings()
        initial_filtered = [
            meeting for meeting in meetings
            if meeting.review_state == 'planned'
            or (meeting.getStart_time and not meeting.getStart_time.isPast())
            ]
        # Now we need the objects for another check and we need those
        # in the template anyway.
        objects = [meeting.getObject() for meeting in initial_filtered]
        filtered = [obj for obj in objects if self.mtool.checkPermission(
            'minaraad.projects: view meeting in digibib', obj)]
        return self._sort_meetings(filtered)

    def organize_by_year(self, objects, get_year, sort_on=None):
        """Organize objects by year.

        'get_year' is a function that gets the year for one object.

        We return a list of objects for the current or chosen year and
        a list of links to other years.
        """
        # group by year
        grouped = {}
        for obj in objects:
            year = get_year(obj)
            if year not in grouped:
                grouped[year] = []

            grouped[year].append(obj)

        # Show the current or requested year only.
        current_year = DateTime().year()
        try:
            year = int(self.request.get('year'))
        except:
            year = current_year

        links = []
        this_year = {}  # Should not be needed, but just in case.
        for res_year, objects in sorted(grouped.items(),
                                        key=lambda g: g[0], reverse=True):
            selected = False
            if res_year == year:
                selected = True
                this_year = {'year': year,
                             'objects': objects}

            links.append(dict(year=res_year,
                              num=len(objects),
                              selected=selected))

        years = [link['year'] for link in links]

        if not this_year:
            # Make a dummy dictionary for this year.  Normally only
            # happens when this is the current year and there are no
            # objects for this year.
            this_year = {'year': year, 'objects': []}
            links.insert(0, {'year': year, 'num': 0, 'selected': True})

        if year != current_year and current_year not in years:
            links.insert(0, {'year': current_year, 'num': 0,
                             'selected': False})

        if sort_on is not None:
            this_year['objects'] = sorted(this_year['objects'], key = sort_on)

        return this_year, links


class MeetingsListingView(DigiBibView):
    """ Sub-view displaying all meetings.
    """

    def show_future_meetings(self):
        """Show future meetings?

        Only show this when we show the current year.
        """
        try:
            year = int(self.request.get('year'))
        except:
            # No year or wrong year.
            return True
        return year == DateTime().year()

    def get_past_meetings(self):
        objects = self._sort_meetings(
            [meeting for meeting in self.context.list_meetings()
             if meeting.getStart_time and
             meeting.getStart_time.isPast()], brains=True, reverse=True)

        def get_year(x):
            return x.getStart_time.year()

        return self.organize_by_year(objects, get_year)

    def get_future_meetings(self):
        return self._sort_meetings(
            [meeting for meeting in self.context.list_meetings()
             if meeting.getStart_time and
             not meeting.getStart_time.isPast()], brains=True)


class ProjectsListingView(DigiBibView):
    """ Sub-view displaying all projects.
    """

    def get_projects(self):
        brains = self._sort_projects(
            self.list_all_projects(), reverse=True)

        # Since we sort on advisory date now, we must organize by the
        # year of that date too, instead of the year of the deadline.
        get_year = lambda x: x.getAdvisory_date.year()
        sort_on = lambda x: x.getProject_number

        return self.organize_by_year(brains, get_year, sort_on)


class OrganisationsListingView(DigiBibView):
    """ Sub-view displaying all organisations.
    """

    def get_organisations(self):
        return sorted(self.context.list_organisations(),
                      key=lambda x: x.Title())
