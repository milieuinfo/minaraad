from datetime import date
from zope.i18n import translate
from Products.validation.interfaces import ivalidator

from minaraad.projects import MinaraadProjectMessageFactory as _


class ProjectIdValidator:
    """ Ensures that the ID entered for a project corresponds to a
    date.

    >>> validator = ProjectIdValidator('my_validator')
    >>> validator('20101005')
    True

    It expects numbers of course:
    >>> validator('YYYYMMDD')
    u'Project id must be of the form YYYYMMDD'

    It expects '0' before the numbers:
    >>> validator('201022')
    u'Project id must be of the form YYYYMMDD'

    And it also check date really exists:
    >>> validator('20100231')
    u'Project id must be of the form YYYYMMDD'
    """
    __implements__ = (ivalidator, )

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        msg = _('Project id must be of the form YYYYMMDD')
        try:
            year = int(value[0:4])
            month = int(value[4:6])
            day = int(value[6:8])
            date(year, month, day)
        except ValueError:
            return translate(msg, context=kwargs.get('REQUEST', None))

        return True


class ProjectNumberValidator:
    """ Just ensures we get a three digits entry.

    >>> validator = ProjectNumberValidator('my_validator')
    >>> validator('123')
    True

    >>> validator('000')
    True

    >>> validator('0')
    u'Number must be 3-digits'

    >>> validator('1234')
    u'Number must be 3-digits'

    >>> validator('0a1')
    u'Number must be 3-digits'
    """

    __implements__ = (ivalidator, )

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        msg = _('Number must be 3-digits')
        try:
            if len(value) != 3:
                raise Exception
            digits = [str(x) for x in range(0, 10)]

            for d in value:
                if not d in digits:
                    raise Exception

        except:
            return translate(msg, context=kwargs.get('REQUEST', None))

        return True
