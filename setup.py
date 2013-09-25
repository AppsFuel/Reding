from setuptools import setup, find_packages, os

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
for m in ('multiprocessing', 'billiard'):
    try:
        __import__(m)
    except ImportError:
        pass

readme = open(os.path.join(os.path.dirname(__file__), 'README.md'),'r').readlines()
description = readme[6]
long_description = ''.join(readme)

tests_require = open(os.path.join(os.path.dirname(__file__), 'test_requirements.txt')).read()
install_requires = open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read()

setup(
    name='Reding',
    version='2.0',
    author='Giorgio Salluzzo',
    author_email='giorgio.salluzzo@gmail.com',
    url='http://buongiornomip.github.com/Reding/',
    maintainer='Giorgio Salluzzo',
    maintainer_email='giorgio.salluzzo@gmail.com',
    description=description,
    long_description=long_description,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
    },
    test_suite='runtests.runtests',
    packages=find_packages(exclude=('tests', )),
    license='The MIT License (MIT)',
    keywords='Rating REST Redis Flask',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ),
)
