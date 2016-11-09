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

import logging
import os
import shutil

from xdg import BaseDirectory

import snapcraft
from snapcraft import file_utils


logger = logging.getLogger(__name__)

"""
We need a generic base class in some place like snapcraft.interal.cache which
would have the building blocks for other modules to add their caching logic.

The base class should take care of cache location, notification and pruning
(we can leave some of these as nops for now).
"""

"""
Consider:

Snap revisions for delta uploads
stage-packages cache
parts cache
Should be automatic based on the number of hits it has.
"""

class SnapcraftCache:
    """Generic cache base class.

    This class is responsible for cache location, notification and pruning.
    """

    def __init__(self):
        self.cache_root = os.path.join(
            BaseDirectory.xdg_cache_home, 'snapcraft')
        self.project_cache_root = os.path.join(
            self.cache_root, snapcraft.internal.load_config().data['name'])

    def cache(self):
        pass

    def prune(self):
        pass


class SnapCache(SnapcraftCache):
    """Cache for snap revisions."""

    def _setup_snap_cache(self):
        snap_cache_path = os.path.join(self.project_cache_root, 'revisions')
        os.makedirs(snap_cache_path, exist_ok=True)
        return snap_cache_path

    def cache(self, snap_filename, revision):
        """Cache snap revision in XDG cache.

        :returns: path to cached revision.
        """
        snap_cache_dir = self._setup_snap_cache()

        cached_snap = rewrite_snap_filename_with_revision(
            snap_filename,
            revision)
        cached_snap_path = os.path.join(snap_cache_dir, cached_snap)
        try:
            shutil.copyfile(snap_filename, cached_snap_path)
        except OSError:
            logger.warning(
                'Unable to cache snap {}.'.format(cached_snap))
        return cached_snap_path


def rewrite_snap_filename_with_revision(snap_file, revision):
    splitf = os.path.splitext(snap_file)
    snap_with_revision = '{base}_{rev}{ext}'.format(
        base=splitf[0],
        rev=revision,
        ext=splitf[1])
    return snap_with_revision
