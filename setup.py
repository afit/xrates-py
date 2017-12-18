from distutils.command.install import INSTALL_SCHEMES
from pprint import pprint
from distutils.command.install_data import install_data
from setuptools import setup
import os
import re
import sys

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        line = line.strip()

        if line.startswith('#'):
            # This line is a comment
            continue

        if line.startswith('git'):
            # git dependency, not from pypy
            # should be of the form
            # git+https://github.com/robot-republic/python-s3#python-s3==1.0.0
            if '#' in line:
                pkg = line.split('#')[-1]
            else:
                raise Exception('You haven\'t supplied the package name / version information that this git repository represents.')

            requirements.append(pkg)
        elif line.startswith('-e'):
            # -e path/to/some/project This is pip's "editable" install
            requirements.append(re.sub(r'-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            # This is pip's "find links", I guess we don't support that..
            pass
        else:
            requirements.append(line)

    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        line = line.strip()
        match = re.match(r'git\+(\w+)', line)
        if match:
            protocol = match.groups()[0] # http or ssh
            branch = 'master'
            if '@' in line:  # git+https://github.com/robot-republic/python-s3@some-branch#python-s3
                branch = line.split('@')[1].split('#')[0]
            package_info = line.split('#')[1]
            package, version = package_info.split('==')

            url_base = line.split('#')[0].split('@')[0].rstrip('/')
            if protocol == 'ssh':
                url = url_base + '@%s' % branch
            else:
                # Remove any reference to git, and alter to tarball
                # the first 4 characters are "git+", remove then
                url_base = url_base[4:]
                url = '/'.join([url_base, 'tarball', branch])
                url = url.replace('https', 'http')


            egg = '%s-%s' % (package, version)
            dependency_links.append('%s#egg=%s' % (url,  egg))

    return dependency_links






REQS = os.path.join(os.path.dirname(__file__), 'requirements.txt')

#print parse_requirements(REQS)
#print parse_dependency_links(REQS)

# From https://github.com/django/django/blob/master/setup.py

class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific fix
    # for this in distutils.command.install_data#306. It fixes install_lib but not
    # install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to the
        # fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}

core_dir = 'xrates'
packages = []
data_files = []

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for dirpath, dirnames, filenames in os.walk(core_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup(
    name='xrates',
    version='0.1',
    packages = packages,
    cmdclass = cmdclasses,
    data_files = data_files,
    url='https://github.com/afit/xrates-py',
    install_requires = parse_requirements(REQS),
    dependency_links = parse_dependency_links(REQS),
    license='',
    author='',
    author_email='',
    description='',
    package_data={'xrates': ['dev/*', ]},
)
