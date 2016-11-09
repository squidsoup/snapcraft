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

import logging

import fixtures

from snapcraft import tests
from snapcraft.internal import cache


class SnapCacheTestCase(tests.TestCase):

    def setUp(self):
        super().setUp()
        self.fake_logger = fixtures.FakeLogger(level=logging.INFO)

    def test_rewrite_snap_filename(self):
        revision = 10
        snap_file = 'my-snap_0.1_amd64.snap'

        self.assertEqual(
            'my-snap_0.1_amd64_10.snap',
            cache.rewrite_snap_filename_with_revision(snap_file, revision))

    def test_snap_cache(self):
        snap_cache = SnapCache()
        # create snap

        # cache snap

        # confirm expected snap cached
