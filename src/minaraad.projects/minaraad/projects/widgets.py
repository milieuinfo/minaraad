from Products.Archetypes import Widget
from AccessControl import ClassSecurityInfo

PARTICIPANT_PRESENT = 0
PARTICIPANT_EXCUSED = 1
PARTICIPANT_ABSENT = 2


class ParticipantsWidget(Widget.LinesWidget):
    security = ClassSecurityInfo()
    _properties = Widget.TypesWidget._properties.copy()
    _properties.update({
        'macro': "participants_widget"
    })

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        vocabulary = getattr(instance, field.vocabulary)()
        participants = []
        for p in vocabulary():
            try:
                value = form.get('%s-%s' % (field.getName(), p), '')
            except ValueError:
                value = PARTICIPANT_ABSENT
            participants.append((p, value))

        return participants, {}
