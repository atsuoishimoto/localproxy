import os, sys
from setuptools import setup, find_packages

def read(fname):
    return open(
            os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "localproxy",
    version = "0.0.3",
    description="HTTP proxy server in twisted. If there is a directory with same name as target host (e.g.: www.example.com), contents of the directory are returned instead of making a request to the target host.",
    url='https://github.com/atsuoishimoto/localproxy',
    author='Atsuo Ishimoto',
    author_email='ishimoto@gembook.org',
    long_description=read('README.rst'),
    classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Internet :: Proxy Servers",
            "Topic :: Software Development :: Debuggers",
            "License :: OSI Approved :: MIT License", ],
    license='MIT License',
    install_requires=['twisted', 'PyOpenSSL', 'service_identity'],
    packages = find_packages(),
    entry_points = """\
      [console_scripts]
      localproxy = localproxy.main:main
    """,
)
