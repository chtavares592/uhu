# Copyright (C) 2017 O.S. Systems Software LTDA.
# SPDX-License-Identifier: GPL-2.0

from prompt_toolkit.validation import ValidationError


class CancelPromptException(Exception):
    """Exception that must be raised when user types Ctrl C."""
    pass


class ValidationError(ValidationError):  # pylint: disable=function-redefined
    """Same as prompt_toolkit, but with extra message appended."""

    def __init__(self, *args, **kwargs):
        msg = kwargs.get('message', '')
        kwargs['message'] = '{}. Type Ctrl-C to cancel.'.format(msg)
        super().__init__(*args, **kwargs)
