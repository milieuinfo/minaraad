from plone.app.users.browser.personalpreferences import UserDataPanel


class CustomizedUserDataPanel(UserDataPanel):

    def __init__(self, context, request):
        super(CustomizedUserDataPanel, self).__init__(context, request)

        omited_fields = ['home_page', 'description',
                         'location', 'portrait', 'pdelete']
        for f_name in omited_fields:
            self.form_fields = self.form_fields.omit(f_name)
