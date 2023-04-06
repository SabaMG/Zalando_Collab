# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------- #

"""
spacescraper.exceptions
------------------------
This file contains the set of spacescraper exceptions.
"""

# ------------------------------------------------------------------------------- #

class CSRF_Exception(Exception):
    '''
    Raise an exception for not finding a csrf-token
    '''

class FormKey_Exception(Exception):
    '''
    Raise an exception for not finding a form-key
    '''

class GetInput_Exception(Exception):
    '''
    Raise an exception for not finding an input
    '''