import itertools

from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


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
        # Note: we used to sort on deadline, but now on advisory date.
        return sorted(p, key=lambda x: x.getAdvisory_date(), reverse=reverse)

    def list_projects(self):
        project_brains = self.ctool(
            {'portal_type': 'Project',
             'review_state': ['in_consideration', 'active', 'finished']})
        projects = [p.getObject() for p in project_brains]
        filtered = [p for p in projects
                    if self.mtool.checkPermission(
                        'minaraad.projects: view project in digibib', p)]

        return self._sort_projects(filtered)

    def list_all_projects(self):
        project_brains = self.ctool({'portal_type': 'Project'})
        projects = [p.getObject() for p in project_brains]
        filtered = [p for p in projects
                    if self.mtool.checkPermission(
                        'minaraad.projects: view project in digibib', p)]

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
            if meeting.getStart_time and \
            not meeting.getStart_time.isPast()]
        # Now we need the objects for another check and we need those
        # in the template anyway.
        objects = [meeting.getObject() for meeting in initial_filtered]
        filtered = [obj for obj in objects if self.mtool.checkPermission(
            'minaraad.projects: view meeting in digibib', obj)]
        return self._sort_meetings(filtered)

    def organize_by_year(self, objects, get_year):
        """Organize objects by year.

        'get_year' is a function that gets the year for one object.

        We return a list of objects for the current or chosen year and
        a list of links to other years.
        """
        # group by year
        grouped = itertools.groupby(objects, get_year)
        # Turn it into a dict, as that is easier for the template
        results = [dict(year=year, objects=[i for i in objects])
                   for year, objects in grouped]

        # Show the current or requested year only.
        current_year = DateTime().year()
        try:
            year = int(self.request.get('year'))
        except:
            year = current_year
        links = []
        this_year = {}  # Should not be needed, but just in case.
        for result in results:
            selected = False
            if result['year'] == year:
                selected = True
                this_year = result
            links.append(dict(year=result['year'],
                               num=len(result['objects']),
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
              [meeting.getObject() for meeting in self.context.list_meetings()
                if meeting.getStart_time and \
                meeting.getStart_time.isPast()], reverse=True)

        def get_year(x):
            return x.getStart_time().year()

        return self.organize_by_year(objects, get_year)

    def get_future_meetings(self):
        return self._sort_meetings(
            [meeting.getObject() for meeting in self.context.list_meetings()
             if meeting.getStart_time and \
             not meeting.getStart_time.isPast()])


class ProjectsListingView(DigiBibView):
    """ Sub-view displaying all projects.
    """

    def get_projects(self):
        objects = self._sort_projects(
            self.context.list_all_projects(), reverse=True)

        # Since we sort on advisory date now, we must organize by the
        # year of that date too, instead of the year of the deadline.
        get_year = lambda x: x.getAdvisory_date().year()

        return self.organize_by_year(objects, get_year)


class OrganisationsListingView(DigiBibView):
    """ Sub-view displaying all organisations.
    """

    def get_organisations(self):
        return sorted(self.context.list_organisations(),
                      key=lambda x: x.Title())
