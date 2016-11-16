# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016 Canonical Ltd
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
import fixtures
import random

from testtools import TestCase
from testtools import matchers as m

from snapcraft.internal.deltas import XdeltaGenerator
from snapcraft.internal.deltas import _deltas


class XdeltaTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.workdir = self.useFixture(fixtures.TempDir()).path
        self.source_file = os.path.join(self.workdir, 'source.snap')
        self.target_file = os.path.join(self.workdir, 'target.snap')

        with open(self.source_file, 'wb') as f:
            f.write(b'This is the source file.')
        with open(self.target_file, 'wb') as f:
            f.write(b'This is the target file.')

    def generate_snap_pair(self):
        """Generate more realistic snap data.

        Most tests don't need realistic data, and can use the default dummy
        data that's created by setUp. However, tests that actually run xdelta
        or bsdiff could use more accurate data. This file generates larger
        binary files. The files will be similar with roughly 0.1 variance along
        1KB block boundaries.
        """
        mean_size = 2**20
        size_stddev = 2**15
        snap_size = int(random.normalvariate(mean_size, size_stddev))

        scratchdir = self.useFixture(fixtures.TempDir()).path
        self.source_path = os.path.join(scratchdir, 'source-snap')
        self.target_path = os.path.join(scratchdir, 'target-snap')
        # source snap is completely random:
        with open(self.source_path, 'wb') as source, \
                open(self.target_path, 'wb') as target:
            for i in range(0, snap_size, 1024):
                block = os.urandom(1024)
                source.write(block)
                if random.randint(0, 9) == 0:
                    target.write(os.urandom(1024))
                else:
                    target.write(block)

    def test_raises_DeltaGenerationFailed_when_xdelta_not_installed(self):
        self.patch(_deltas, 'executable_exists', lambda a: False)
        self.patch(_deltas, 'which', lambda a: None)

        self.assertThat(
            lambda: XdeltaGenerator(self.source_file, self.target_file),
            m.raises(_deltas.DeltaGenerationFailed)
        )

    def test_xdelta(self):
        self.generate_snap_pair()
        base_delta = XdeltaGenerator(self.source_file, self.target_file)
        path = base_delta.make_delta()

        self.assertThat(path, m.FileExists())

    def test_xdelta_logs(self):
        logger = self.useFixture(fixtures.FakeLogger())

        self.generate_snap_pair()
        base_delta = XdeltaGenerator(self.source_file, self.target_file)
        base_delta.make_delta()


        self.assertThat(
            logger.output,
            m.Contains('Generating xdelta delta for {}->{}.'.format(
                base_delta.source_path, base_delta.target_path)))
