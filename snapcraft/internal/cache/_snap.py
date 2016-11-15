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

from snapcraft.internal.cache._cache import SnapcraftProjectCache
from snapcraft._store import latest_rev


logger = logging.getLogger(__name__)


class SnapCache(SnapcraftProjectCache):
    """Cache for snap revisions."""
    def __init__(self):
        super().__init__()
        self.snap_cache_dir = self._setup_snap_cache()

    def _setup_snap_cache(self):
        snap_cache_path = os.path.join(self.project_cache_root, 'revisions')
        os.makedirs(snap_cache_path, exist_ok=True)
        return snap_cache_path

    def cache(self, snap_filename, revision):
        """Cache snap revision in XDG cache.

        :returns: path to cached revision.
        """
        snap_cache_dir = self._setup_snap_cache()

        cached_snap = _rewrite_snap_filename_with_revision(
            snap_filename,
            revision)
        cached_snap_path = os.path.join(snap_cache_dir, cached_snap)
        try:
            shutil.copyfile(snap_filename, cached_snap_path)
        except OSError:
            logger.warning(
                'Unable to cache snap {}.'.format(cached_snap))
        return cached_snap_path

    def prune(self, revision=None):
        """Prune the snap revisions beside the head revision in XDG cache."""

        name = self.config.data['name']
        arch = self.config.data['architectures']

        if revision is None:

            # get the latest history info from store if
            # revision is not specified
            latest_history = latest_rev(snap_name=name, arch=arch)
            revision = latest_history['revision']

        for snap_filename in os.listdir(self.snap_cache_dir):
            cached_snap = os.path.join(self.snap_cache_dir, snap_filename)

            # get the file version from file name
            rev_from_snap_file = _get_revision_from_snap_filename(
                snap_filename)

            if rev_from_snap_file != revision:
                try:
                    os.remove(cached_snap)
                except OSError:
                    logger.warning(
                        'Unable to purge snap {}.'.format(cached_snap))


def _rewrite_snap_filename_with_revision(snap_file, revision):
    splitf = os.path.splitext(snap_file)
    snap_with_revision = '{base}_{rev}{ext}'.format(
        base=splitf[0],
        rev=revision,
        ext=splitf[1])
    return snap_with_revision


def _get_revision_from_snap_filename(snap_filename):
    """parse the filename to extract the revision info"""
    # the cached snap filename should have the format:
    # '{name}_{version}_{arch}_{revision}.snap'
    filename, extname = os.path.splitext(snap_filename)
    split_name_parts = filename.split('_')
    if len(split_name_parts) != 4:
        logger.debug('The cached snap filename {} is invalid.'.format(
            snap_filename))
        return None

    try:
        rev = int(split_name_parts[-1])
    except ValueError:
        logger.debug('The cached snap filename has invalid revision.')
        return None
    return rev
