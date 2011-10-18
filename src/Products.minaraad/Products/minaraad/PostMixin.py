# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

schema = atapi.Schema((
),
)

PostMixin_schema = schema.copy()


class PostMixin:
    """
    """
    security = ClassSecurityInfo()

    allowed_content_types = []
    _at_rename_after_creation = True

    schema = PostMixin_schema
