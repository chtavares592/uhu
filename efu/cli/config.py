# Copyright (C) 2016 O.S. Systems Software LTDA.
# This software is released under the MIT License

import click

from ..config import config


@click.group(name='config')
def config_cli():
    ''' Configures efu utility. '''
    pass


@config_cli.command()
def init():
    ''' Sets efu required initial configuration. '''
    access_id = input('EasyFOTA Access Key ID: ')
    access_secret = input('EasyFota Systems Secret Access Key: ')
    config.set_initial(access_id, access_secret)


@config_cli.command(name='set')
@click.argument('entry')
@click.argument('value')
@click.option('--section', help='Section to write the configuration')
def set_(entry, value, section):
    '''
    Sets the given VALUE in a configuration ENTRY.
    '''
    config.set(entry, value, section=section)


@config_cli.command()
@click.argument('entry')
@click.option('--section', help='Section to write the configuration')
def get(entry, section):
    '''
    Gets the value from a given ENTRY.
    '''
    value = config.get(entry, section=section)
    if value:
        print(value)