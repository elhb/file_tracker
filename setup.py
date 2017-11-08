from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
 # Extension(
 #     'filetracker.config',
 #     ['filetracker/config.pyx']
 # )
]

reqs = [line.rstrip() for line in open('requirements.txt')]
packages = find_packages()

setup(name='file_tracker',
    version='0.0.1-alpha',
    description="",
    url='https://github.com/elhb/file_tracker',
    author='Erik Borgstroem',
    author_email='eriklhb@gmail.com',
    packages=packages,
    include_package_data=True,
    setup_requires=["Cython >= 0.25.2"],
    install_requires=reqs,
    scripts=[
        'track_files'
        ],
    ext_modules=cythonize(extensions)
)