import os
import sys

from setuptools import setup, find_packages

setup(

    # Vitals
    name='amalthea',
    license='BSD',
    url='https://github.com/greatscottgadgets/amalthea',
    author='Mike Walters',
    author_email='mike@flomp.net',
    description='',
    use_scm_version= {
        "root": '..',
        "relative_to": __file__,
        "version_scheme": "guess-next-dev",
        "local_scheme": lambda version : version.format_choice("+{node}", "+{node}.dirty"),
        "fallback_version": "0.0"
    },

    # Imports / exports / requirements.
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    python_requires="~=3.7",
    install_requires=[
        'amaranth @ git+https://github.com/amaranth-lang/amaranth.git',
        'amaranth_boards @ git+https://github.com/amaranth-lang/amaranth-boards.git',
        'amaranth_soc @ git+https://github.com/amaranth-lang/amaranth-soc.git',
        'luna @ git+https://github.com/greatscottgadgets/luna.git',
    ],
    setup_requires=['setuptools', 'setuptools_scm'],

    # Metadata
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Security',
        ],
)
