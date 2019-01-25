import os

import reframe as rfm
import reframe.utility.sanity as sn

@rfm.required_version('>=2.14')
@rfm.simple_test
class CPMDCheck(rfm.RunOnlyRegressionTest):
    def __init__(self):
        super().__init__()
        self.descr = 'CPMD check (C4H6 metadynamics)'
        self.maintainers = ['AJ', 'LM']
        self.tags = {'production'}

        self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_prog_environs = ['PrgEnv-intel']
        self.modules = ['CPMD']
        self.executable = 'cpmd.x'
        self.executable_opts = ['ana_c4h6.in > stdout.txt']
        self.readonly_files = ['ana_c4h6.in', 'C_MT_BLYP', 'H_MT_BLYP']
        if self.current_system.name == 'dom':
            self.num_tasks = 9
        else:
            self.num_tasks = 16
        self.num_tasks_per_node = 1
        self.use_multithreading = True
        self.strict_check = False
        self.extra_resources = {
            'switches': {
                'num_switches': 1
            }
        }
        #  OpenMP version of CPMD segfaults
        #  self.variables = { 'OMP_NUM_THREADS' : '8' }
        energy = sn.extractsingle(
            r'CLASSICAL ENERGY\s+-(?P<result>\S+)',
            'stdout.txt', 'result', float)
        energy_reference = 25.81
        energy_diff = sn.abs(energy - energy_reference)
        self.sanity_patterns = sn.assert_lt(energy_diff, 0.26)
        self.perf_patterns = {
            'perf': sn.extractsingle(r'^ cpmd(\s+[\d\.]+){3}\s+(?P<perf>\S+)',
                                     'stdout.txt', 'perf', float)
        }

        self.reference = {
            'daint:gpu': {
                'perf': (245.0, None, 0.59)   # (225.0, None, 0.15)
            },
            'dom:gpu': {
                'perf': (332.0, None, 0.15)
            },
        }

