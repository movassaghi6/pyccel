# coding: utf-8

"""
This file contains some useful functions to compile the generated fortran code
"""

import os
import subprocess
import sys

__all__ = ['construct_flags', 'compile_files']

#==============================================================================
# TODO use constructor and a dict to map flags w.r.t the compiler
_avail_compilers = ['gfortran', 'mpif90', 'pgfortran', 'ifort', 'gcc', 'icc']

language_extension = {'fortran':'f90', 'c':'c', 'python':'py'}

#==============================================================================
# TODO add opt flags, etc... look at f2py interface in numpy
def construct_flags(compiler,
                    fflags=None,
                    debug=False,
                    accelerator=None,
                    includes=(),
                    libdirs=()):
    """
    Constructs compiling flags for a given compiler.

    fflags: str
        Fortran compiler flags. Default is `-O3`

    compiler: str
        used compiler for the target language.

    accelerator: str
        name of the selected accelerator.
        One among ('openmp', 'openacc')

    debug: bool
        add some useful prints that may help for debugging.

    includes: list
        list of include directories paths

    libdirs: list
        list of lib directories paths
    """

    if not(compiler in _avail_compilers):
        raise ValueError("Only {0} are available.".format(_avail_compilers))

    if not fflags:
        fflags = '-O3'

    # make sure there are spaces
    flags = str(fflags)
    if compiler == "gfortran":
        if debug:
            flags += " -fcheck=bounds"

    if compiler == "mpif90":
        if debug:
            flags += " -fcheck=bounds"
        if sys.platform == "win32":
            mpiinc = os.environ["MSMPI_INC"].rstrip('\\')
            mpilib = os.environ["MSMPI_LIB64"].rstrip('\\')
            flags += ' -D USE_MPI_MODULE -I"{}" -L"{}"'.format(mpiinc, mpilib)

    if accelerator is not None:
        if accelerator == "openmp":
            flags += " -fopenmp"
        elif accelerator == "openacc":
            flags += " -ta=multicore -Minfo=accel"
        else:
            raise ValueError("Only openmp and openacc are available")

    # Construct flags
    flags += ''.join(' -I"{0}"'.format(i) for i in includes)
    flags += ''.join(' -L"{0}"'.format(i) for i in libdirs)

    return flags

#==============================================================================
def compile_files(filename, compiler, flags,
                    binary=None,
                    verbose=False,
                    modules=[],
                    is_module=False,
                    libs=(),
                    language="fortran",
                    output=''):
    """
    Compiles the generated file.

    verbose: bool
        talk more
    """

    if binary is None:
        if not is_module:
            binary = os.path.splitext(os.path.basename(filename))[0]
            mod_file = ''
        else:
            f = os.path.join(output, os.path.splitext(os.path.basename(filename))[0])
            binary = '{}.o'.format(f)
#            binary = "{folder}{binary}.o".format(folder=output,
#                                binary=os.path.splitext(os.path.basename(filename))[0])
            mod_file = '"{folder}"'.format(folder=output)

    o_code = '-o'
    j_code = ''
    if is_module:
        flags += ' -c '
        if (len(output)>0) and language == "fortran":
            j_code = '-J'

    m_code = ' '.join('{}.o'.format(m) for m in modules)
    libs_flags = ' '.join('-l{}'.format(i) for i in libs)

    filename = '"{}"'.format(filename)  # in case of spaces in path
    binary = '"{}"'.format(binary)

    if sys.platform == "win32" and compiler == "mpif90":
        compiler = "gfortran"
        filename += ' "{}"'.format(os.path.join(os.environ["MSMPI_LIB64"], 'libmsmpi.a'))

    cmd = '{0} {1} {2} {3} {4} {5} {6} {7} {8}'.format( \
        compiler, flags, m_code, filename, o_code, binary, libs_flags, j_code, mod_file)

    if verbose:
        print(cmd)

    output = subprocess.check_output(cmd, shell=True)

    if output:
        print(output)

    # TODO shall we uncomment this?
#    # write and save a log file in .pyccel/'filename'.log
#    # ...
#    def mkdir_p(dir):
#        # type: (unicode) -> None
#        if os.path.isdir(dir):
#            return
#        os.makedirs(dir)
#
#    if True:
#        tmp_dir = '.pyccel'
#        mkdir_p(tmp_dir)
#        logfile = '{0}.log'.format(binary)
#        logfile = os.path.join(tmp_dir, logfile)
#        f = open(logfile, 'w')
#        f.write(output)
#        f.close()

    return output, cmd
