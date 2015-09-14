# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile

from snapcraft import repo
from snapcraft import tests


class UbuntuTestCase(tests.TestCase):

    def test_unrecognized_package_raises_exception(self):
        ubuntu = repo.Ubuntu('download_dir')

        with self.assertRaises(repo.PackageNotFoundError) as raised:
            ubuntu.get(['test_package'])

        expected_message = 'The Ubuntu package \'test_package\' was not found'
        self.assertEqual(raised.exception.message, expected_message)

    def test_fix_symlinks(self):
        tempdirObj = tempfile.TemporaryDirectory()
        self.addCleanup(tempdirObj.cleanup)
        tempdir = tempdirObj.name

        os.makedirs(tempdir + '/a')
        open(tempdir + '/1', mode='w').close()

        os.symlink('a', tempdir + '/rel-to-a')
        os.symlink('/a', tempdir + '/abs-to-a')
        os.symlink('/b', tempdir + '/abs-to-b')
        os.symlink('1', tempdir + '/rel-to-1')
        os.symlink('/1', tempdir + '/abs-to-1')

        repo._fix_symlinks(debdir=tempdir)

        self.assertEqual(os.readlink(tempdir + '/rel-to-a'), 'a')
        self.assertEqual(os.readlink(tempdir + '/abs-to-a'), 'a')
        self.assertEqual(os.readlink(tempdir + '/abs-to-b'), '/b')
        self.assertEqual(os.readlink(tempdir + '/rel-to-1'), '1')
        self.assertEqual(os.readlink(tempdir + '/abs-to-1'), '1')