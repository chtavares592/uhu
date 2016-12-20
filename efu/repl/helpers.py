# Copyright (C) 2016 O.S. Systems Software LTDA.
# This software is released under the MIT License
"""EFU REPL helper functions.

Includes reusable prompts, auto-completers, constraint checkers.
"""

import sys
from functools import partial, wraps

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys

from ..core.validators import validate_option_requirements
from ..core.object import Modes
from ..core._options import Options
from ..core.package import MODES as PKG_MODES
from ..utils import indent

from .completers import (
    ObjectFilenameCompleter, ObjectModeCompleter, ObjectOptionCompleter,
    ObjectOptionValueCompleter, ObjectUIDCompleter, YesNoCompleter,
    PackageModeCompleter)
from .exceptions import CancelPromptException
from .validators import (
    ObjectUIDValidator, ContainerValidator, ObjectOptionValueValidator,
    PackageUIDValidator, YesNoValidator)


manager = KeyBindingManager.for_prompt()


@manager.registry.add_binding(Keys.ControlD)
def ctrl_d(event):
    """Ctrl D quits appliaction returning 0 to sys."""
    event.cli.run_in_terminal(sys.exit(0))


@manager.registry.add_binding(Keys.ControlC)
def ctrl_c(_):
    """Ctrl C raises an exception to be caught by functions.

    Main prompt must exit efu with code status 1, while subprompts
    must returns to main prompt.
    """
    raise CancelPromptException('Cancelled operation.')


def cancellable(f):
    """Decorator to cancell a current prompt."""
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except CancelPromptException:
            pass  # Do nothing cancelling the current command
    return wrapper


prompt = partial(prompt, key_bindings_registry=manager.registry)


def check_arg(ctx, msg):
    """Checks if user has passed an argument.

    :param msg: The error message to display to the user in when an
                argument is not passed.
    """
    if ctx.arg is None:
        raise ValueError(msg)


def check_version(ctx):
    """Checks if package already has a version."""
    if ctx.package.version is None:
        raise ValueError('You need to set a version first')


def check_product(ctx):
    """Checks if product is already set."""
    if ctx.package.product is None:
        raise ValueError('You need to set a product first')


def set_product_prompt(product):
    """Sets prompt to be 'efu [product]'."""
    return '[{}] efu> '.format(product[:6])


def parse_prompt_object_uid(value):
    """Parses value passed to a prompt using get_objects_completer.

    :param value: A value returned by :func:`get_objects_completer`.
    """
    return int(value.split('#')[0].strip())


def prompt_object_options(package_mode, object_mode):
    """Prompts user for object options.

    :param pacakge_mode: A efu `InstallationSetMode` instance.
    :param object_mode: A string indicating the object mode.
    """
    options = {}
    mode = Modes.get(object_mode)
    for option in [opt for opt in mode.options if not opt.volatile]:
        try:
            validate_option_requirements(option, options)
        except ValueError:
            continue  # requirements not satisfied, skip this option
        if option.symmetric:
            value = prompt_object_option_value(option, object_mode)
        else:
            value = []
            for installation_set in range(package_mode.value):
                default = value[-1] if len(value) else ''
                value.append(
                    prompt_object_option_value(
                        option=option,
                        mode=object_mode,
                        installation_set=installation_set,
                        default=default,
                    ))
            value = tuple(value)
        options[option.metadata] = value
    return options


def prompt_object_mode():
    """Prompts user for a object mode."""
    msg = 'Choose a mode: '
    completer = ObjectModeCompleter()
    validator = ContainerValidator('mode', Modes.names())
    mode = prompt(msg, completer=completer, validator=validator)
    return mode.strip()


def prompt_object_uid(package, installation_set=None):
    """Prompts user for an object UID.

    :param index: The object index within an object list.
    """
    if installation_set is None:
        installation_set = 0
    msg = 'Select an object: '
    completer = ObjectUIDCompleter(package, installation_set)
    validator = ObjectUIDValidator()
    value = prompt(msg, completer=completer, validator=validator)
    return parse_prompt_object_uid(value.strip())


def prompt_object_option(obj):
    """Prompts user for a valid option for the given object.

    :param obj: an efu `Object` instance.
    """
    msg = 'Choose an option: '
    options = sorted(opt.metadata for opt in obj.options if not opt.symmetric)
    completer = ObjectOptionCompleter(options)
    validator = ContainerValidator('option', options)
    option = prompt(msg, completer=completer, validator=validator)
    return Options.get(option.strip())


def _get_object_option_value_message(option, indent_level, set_=None):
    """Retuns a message for object_option_value prompt."""
    if option.default is not None:
        default_msg = option.default
        if option.type_name == 'boolean':
            if default_msg:
                default_msg = 'Y/n'
            else:
                default_msg = 'y/N'
        msg = '{} [{}]'.format(option.verbose_name.title(), default_msg)
    else:
        msg = '{}'.format(option.verbose_name.title())
    msg = indent(msg, indent_level, all_lines=True)
    set_msg = ''
    if set_ is not None:
        set_msg = ' (installation set {})'.format(set_)
    msg = '{}{}: '.format(msg, set_msg)
    return msg


def _prompt_object_option_value(option, msg, completer, default, validator):
    """Retuns a value for object_option_value prompt."""
    value = prompt(
        msg, completer=completer, default=default, validator=validator).strip()
    if value == '':
        return option.default
    return option.validate(value)


def _get_object_option_value_completer(option):
    """Retuns a completer for object_option_value prompt."""
    if option.choices:
        return ObjectOptionValueCompleter(option)
    elif option.type_name == 'boolean':
        return YesNoCompleter()
    elif option.metadata == 'filename':
        return ObjectFilenameCompleter()


def prompt_object_option_value(
        option, mode, installation_set=None, default='', indent_level=0):
    """Given an object and an option, prompts user for a valid value.

    :param option: an efu `Option` instance.
    :param mode: a valid Object mode string.
    :param installation_set: an int indicating the installation set.
    :param default: a default value to be displayed as placeholder.
    :param indent_level: Controls how many spaces must be added before
                         `msg`.
    """
    msg = _get_object_option_value_message(
        option, indent_level, installation_set)
    completer = _get_object_option_value_completer(option)
    validator = ObjectOptionValueValidator(option, mode)
    value = _prompt_object_option_value(
        option, msg, completer, default, validator)
    return value


def prompt_package_uid():
    """Prompts user for a package UID."""
    msg = 'Type a package UID: '
    validator = PackageUIDValidator()
    uid = prompt(msg, validator=validator)
    return uid.strip()


def prompt_pull():
    """Prompts user to set if a pull should download all files or not."""
    msg = 'Should we download all files [Y/n]?:  '
    completer = YesNoCompleter()
    validator = YesNoValidator()
    answer = prompt(msg, completer=completer, validator=validator)
    return {'y': True, 'n': False}[answer.strip().lower()[0]]


def prompt_installation_set(package, msg=None):
    """Prompts user for a valid installation set.

    :param package: A core.package.Package instance.
    :param msg: The prompt message to display to user.
    :param all_sets: If True, allow to select an empty installation set.
    """
    if package.objects.is_single():
        return None

    objects = [(index, objs) for index, objs in enumerate(package.objects)]
    indexes = [str(i) for i, _ in objects]

    msg = msg if msg is not None else 'Select an installation set: '
    completer = WordCompleter(indexes)
    validator = ContainerValidator('installation set', indexes)
    installation_set = prompt(msg, completer=completer, validator=validator)
    return int(installation_set.strip())


def prompt_package_mode():
    """Prompts for a valid package mode."""
    msg = 'Choose a package mode [{}]: '.format('/'.join(PKG_MODES))
    completer = PackageModeCompleter()
    validator = ContainerValidator('mode', PKG_MODES)
    mode = prompt(msg, completer=completer, validator=validator)
    return mode.strip().lower()
