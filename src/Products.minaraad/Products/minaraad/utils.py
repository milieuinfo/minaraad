def list_match(l1, l2):
    """ Tells if at least there is one common element
    in the two lists.

    >>> list_match([], [])
    False

    >>> list_match([], ['a', 'b', 'c'])
    False

    >>> list_match(['a', 'b', 'c'], [])
    False

    >>> list_match(['a', 'b', 'c'], ['d', 'e', 'f'])
    False

    >>> list_match(['a', 'b', 'c'], ['d', 'e', 'f', 'b'])
    True

    """
    for el in l1:
        if el in l2:
            return True
    return False
