# Copyright (C) 2017 O.S. Systems Software LTDA.
# SPDX-License-Identifier: GPL-2.0

from uhu.cli.hardware import (
    add_supported_hardware, remove_supported_hardware)
from uhu.core import Package

from cli.test_package import PackageTestCase


class SupportedHardwareCommandsTestCase(PackageTestCase):

    def setUp(self):
        super().setUp()
        self.pkg = Package()
        self.pkg.dump(self.pkg_fn)

    def test_can_add_supported_hardware_identifier(self):
        hardware = 'PowerX'
        result = self.runner.invoke(add_supported_hardware, args=[hardware])
        self.assertEqual(result.exit_code, 0)
        pkg = Package.from_file(self.pkg_fn)
        self.assertEqual(len(pkg.supported_hardware), 1)
        self.assertIn(hardware, pkg.supported_hardware)

    def test_can_remove_supported_hardware_identifier(self):
        hardware = 'PowerX'
        self.pkg.supported_hardware.add(hardware)
        self.pkg.dump(self.pkg_fn)
        pkg = Package.from_file(self.pkg_fn)
        self.assertEqual(len(pkg.supported_hardware), 1)
        result = self.runner.invoke(remove_supported_hardware, args=[hardware])
        self.assertEqual(result.exit_code, 0)
        pkg = Package.from_file(self.pkg_fn)
        self.assertEqual(len(pkg.supported_hardware), 0)

    def test_remove_supported_hardware_returns_2_if_invalid_identifier(self):
        self.pkg.supported_hardware.add('PowerX')
        self.pkg.dump(self.pkg_fn)
        result = self.runner.invoke(remove_supported_hardware, args=['PowerY'])
        self.assertEqual(result.exit_code, 2)
