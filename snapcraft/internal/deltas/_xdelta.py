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
import subprocess

from snapcraft.internal.deltas import BaseDeltasGenerator


logger = logging.getLogger(__name__)


class XDeltaGenerator(BaseDeltasGenerator):

    delta_format = 'xdelta'
    delta_tool_path = '/usr/bin/xdelta'

    def call_delta_generation(self, delta_tool, source_path, target_path,
                              delta_file, stdout_file, stderr_file, workdir):
        process = subprocess.Popen(
            [delta_tool, 'delta', source_path, target_path, delta_file],
            stdout=stdout_file,
            stderr=stderr_file,
            cwd=workdir
        )
        return process

    def log_delta_file(self, delta_file):
        logger.debug(
            "xdelta delta diff generation:\n%s" %
            subprocess.check_output(
                [self.delta_tool_path, 'info', delta_file],
                universal_newlines=True)
            )
