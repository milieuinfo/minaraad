from zExceptions import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.Five import BrowserView
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent

from archetypes.schemaextender.interfaces import ISchemaExtender


class BaseAgendaItemView(BrowserView):
    """ Base view for adding/viewing/editing
    agenda items.
    """
    agenda_fields = ['title', 'duration', 'summary', 'project']
    attachment_fields = ['title', 'file', 'published']

    new_ids = ['new_att_%s_' % i for i in range(0, 3)]

    def __init__(self, *args, **kwargs):
        super(BaseAgendaItemView, self).__init__(*args, **kwargs)
        self.errors = {}

    def get_agenda_item(self):
        return self.context

    def get_attachment_extra_fields(self, attachment):
        extender = ISchemaExtender(attachment)
        return dict([(f.getName(), f) for f in extender.getFields()])

    def redirect_url(self):
        """ URL where the user is redirected after form submission.
        """
        return self.context.absolute_url()

    def get_attachment_form(self, att_id):
        """ Filters the form to keep only the parts describing
        an attachment.
        """
        key = 'att_%s_' % att_id
        return dict(
            [(k.split(key)[-1], w) for k, w in self.request.form.items()
             if k.startswith(key)])

    def filter_archetype_form(self, form, context, schema, fields):
        """ This can be used when you manage Archetypes objects and use
        the archetypes macros in the template.
        This method will use the widgets process_form method to transform
        content in the form.
        """
        new_form = {}
        try:
            extender = ISchemaExtender(context)
            extra_fields = extender.getFields()
        except TypeError:
            extra_fields = []

        for field in schema.fields() + extra_fields:
            fieldname = field.getName()
            if not fieldname in fields:
                continue

            widget = field.widget
            processed_value = widget.process_form(
                context, field, form)

            if isinstance(processed_value, tuple):
                new_form[fieldname] = processed_value[0]
            else:
                new_form[fieldname] = processed_value

        return new_form

    def check_archetype_form(self, form, context, fields, prefix = None):
        """ Uses the schema validators to validate a form.
        """
        for field in context.schema.fields():
            fieldname = field.getName()
            if not fieldname in fields:
                continue

            if fieldname == 'file':
                if form.get('file_delete', None) == 'nochange':
                    # We get an error even when we don't want to change the file ...
                    continue
                elif form['file_file'].filename != '':
                    # We check there's a file name, in that case a file has been
                    # uploaded.
                    continue

            field_errors = field.validate(
                form.get(fieldname),
                context,
                REQUEST=self.request)

            if field_errors is not None:
                if prefix:
                    key = '%s_%s' % (prefix, fieldname)
                else:
                    key = fieldname

                self.errors[key] = field_errors

    def check_form(self):
        """ Returns True if the firm does not contain
        errors.
        Fills self.errors otherwise.
        """
        return True

    def process_form(self):
        """ Should be overriden in sub classes.
        Creates/edit the agenda item. In sub classes, it should
        return a redirection.
        """
        return self.request.response.redirect(
            self.redirect_url())

    def cancelled_form(self):
        """ In sub-classes, returns the redirection when
        the user hits cancel.
        """
        return self.request.response.redirect(
            self.redirect_url())

    def get_attachments(self):
        # We create three new attachments.
        # They will be deleted after if needed.
        for att_id in self.new_ids:
            if not att_id in self.context.contentIds():
                try:
                    self.context.invokeFactory('FileAttachment', id=att_id)
                except Unauthorized:
                    # Apparently we can edit, but not add.
                    break

        return self.context.contentValues()

    def _update_attachment(self, agenda_item, attachment, att_id = None):
        """ Update title/publication/file for an attachment.
        """
        if att_id is None:
            att_id = attachment.id

        form = self.filter_archetype_form(
            self.get_attachment_form(att_id),
            attachment,
            attachment.schema,
            self.attachment_fields)

        if form.get('file', False) is None:
            del form['file']

        attachment.update(**form)
        if attachment.Title() == '':
            attachment.title = attachment.getFile().filename

        attachment.reindexObject()
        notify(ObjectEditedEvent(attachment))

    def _create_attachment(self, agenda_item, att_id):
        """ Create a new attachment in the agenda item.
        """
        filename = self.get_attachment_form(att_id)['file_file'].filename
        if filename in agenda_item.contentIds():
            new_id = self.context.generateUniqueId(filename)
        else:
            new_id = self.context.generateUniqueId('FileAttachment')

        self.context.invokeFactory('FileAttachment',
                                   id = new_id)

        attachment = getattr(agenda_item, new_id)
        attachment.unmarkCreationFlag()
        attachment._renameAfterCreation()
        notify(ObjectInitializedEvent(attachment))
        self._update_attachment(agenda_item, attachment, att_id)

    def add_attachments(self, agenda_item):
        """ Adds attachments from the form.
        """
        for attachment in self.get_attachments():
            if attachment.id in self.new_ids:
                continue

            self._update_attachment(agenda_item, attachment)

        form = self.request.form
        new_attachments = False

        for att_id in self.new_ids:
            if form.get('att_%s_file_file' % att_id):
                new_attachments = True
                self._create_attachment(agenda_item, att_id)

            if att_id in self.context.contentIds():
                # We delete the attachment as it is useless now.
                self.context.manage_delObjects([att_id])

        if new_attachments:
            meeting = aq_parent(aq_inner(agenda_item))
            meeting._update_agenda_item_attachment_counter()

    def delete_temp_attachments(self):
        for att_id in self.new_ids:
            if att_id in self.context.contentIds():
                # We delete the attachment as it is useless now.
                self.context.manage_delObjects([att_id])

    def __call__(self):
        form = self.request.form
        if self.request.get('REQUEST_METHOD') == 'POST':
            if 'form_submitted' in form and self.check_form():
                return self.process_form()

            if 'form_cancelled' in form:
                self.delete_temp_attachments()
                return self.cancelled_form()

        return self.index()


class EditAgendaItemView(BaseAgendaItemView):
    """ View to edit an agenda item.
    """
    mode = 'edit'

    def form_action(self):
        return '%s/edit_agenda_item' % self.context.absolute_url()

    def redirect_url(self):
        return aq_parent(aq_inner(self.context)).absolute_url()


    def check_form(self):
        self.check_archetype_form(self.request.form,
                             self.context,
                             self.agenda_fields)

        self.context.post_validate(self.request, self.errors)

        for attachment in self.context.contentValues():
            if attachment.id in self.new_ids:
                continue

            self.check_archetype_form(self.get_attachment_form(attachment.id),
                                      attachment,
                                      self.attachment_fields,
                                      prefix = 'att_%s' % attachment.id)

        return len(self.errors.keys()) == 0

    def process_form(self):
        form = self.request.form
        self.context.update(**form)

        if self.context.getIn_factory():
            self.context.setIn_factory(False)
            self.context.unmarkCreationFlag()
            self.context._renameAfterCreation()
            notify(ObjectInitializedEvent(self.context))

        self.add_attachments(self.context)

        notify(ObjectEditedEvent(self.context))
        return super(EditAgendaItemView, self).process_form()
