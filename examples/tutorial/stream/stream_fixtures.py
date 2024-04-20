# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import reframe as rfm
import reframe.utility.sanity as sn


class build_stream(rfm.CompileOnlyRegressionTest):
    build_system = 'SingleSource'
    sourcepath = 'stream.c'
    executable = './stream.x'

    @run_before('compile')
    def prepare_build(self):
        omp_flag = self.current_environ.extras.get('omp_flag')
        self.build_system.cflags = ['-O3', omp_flag]


@rfm.simple_test
class stream_test(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['+openmp']
    stream_binary = fixture(build_stream, scope='environment')

    @run_after('setup')
    def set_executable(self):
        self.executable = os.path.join(self.stream_binary.stagedir, 'stream.x')

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Solution Validates', self.stdout)

    @performance_function('MB/s')
    def copy_bw(self):
        return sn.extractsingle(r'Copy:\s+(\S+)', self.stdout, 1, float)

    @performance_function('MB/s')
    def triad_bw(self):
        return sn.extractsingle(r'Triad:\s+(\S+)', self.stdout, 1, float)
