# .. See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from pathlib import Path

from setuptools import setup, find_namespace_packages

with open(Path(__file__).parent / 'README.md') as f:
    readme = f.read()
with open(Path(__file__).parent / 'VERSION') as f:
    version = f.read()


def import_requirements():
    """Import ``requirements.txt`` file located at the root of the repository."""
    with open(Path(__file__).parent / 'requirements.txt') as file:
        return [line.rstrip() for line in file.readlines()]


setup(
    name='ensembl-metadata-admin',
    version=version,
    namespace_packages=['ensembl'],
    packages=find_namespace_packages(where='src', include=['ensembl.production.*']),
    package_dir={'': 'src'},
    url='https://github.com/Ensembl/ensembl-metadata-admin',
    license='APACHE 2.0',
    author='Marc Chakiachvili,Daniel Poppleton,Vinay Kaikala',
    author_email='mchakiachvili@ebi.ac.uk,danielp@ebi.ac.uk,vinay@ebi.ac.uk',
    maintainer='Ensembl Production Team',
    maintainer_email='ensembl-production@ebi.ac.uk',
    description='Ensembl Production metadata Django admin pages',
    python_requires='>=3.8',
    include_package_data=True,
    install_requires=import_requirements(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: APACHE 2.0 License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ]
)
