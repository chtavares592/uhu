# Copyright (C) 2016 O.S. Systems Software LTDA.
# This software is released under the MIT License

from utils import EFUTestCase
from .base import ModeTestCaseMixin


class TarballObjectTestCase(ModeTestCaseMixin, EFUTestCase):
    mode = 'tarball'

    def setUp(self):
        super().setUp()
        self.default_options = {
            'filename': self.fn,
            'target-device': '/dev/sda',
            'target-path': '/usr/bin',
            'filesystem': 'ext4',
        }
        self.default_template = {
            'filename': self.fn,
            'mode': 'tarball',
            'target-device': '/dev/sda',
            'target-path': '/usr/bin',
            'filesystem': 'ext4',
            'format?': False,
        }
        self.default_metadata = {
            'filename': self.fn,
            'mode': 'tarball',
            'target-device': '/dev/sda',
            'target-path': '/usr/bin',
            'filesystem': 'ext4',
            'format?': False,
            'sha256sum': self.sha256sum,
            'size': self.size,
        }

        self.full_options = {
            'filename': self.fn,
            'target-device': '/dev/sda',
            'target-path': '/usr/bin',
            'filesystem': 'ext4',
            'format?': True,
            'format-options': '--foption',
            'mount-options': '--moption',
        }
        self.full_template = {
            'filename': self.fn,
            'mode': 'tarball',
            'target-device': '/dev/sda',
            'target-path': '/usr/bin',
            'filesystem': 'ext4',
            'format?': True,
            'format-options': '--foption',
            'mount-options': '--moption',
        }
        self.full_metadata = {
            'filename': self.fn,
            'mode': 'tarball',
            'target-device': '/dev/sda',
            'target-path': '/usr/bin',
            'filesystem': 'ext4',
            'format?': True,
            'format-options': '--foption',
            'mount-options': '--moption',
            'size': self.size,
            'sha256sum': self.sha256sum,
        }
