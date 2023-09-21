from setuptools import setup
from setuptools import find_packages
from pyrich import __version__ as VERSION


description = 'My own portfolio management service'
project_urls = {
    'Source': 'https://github.com/choi-jiwoo/pyrich',
}
with open('README.md', 'r') as f:
    long_description = f.read()

install_requires = [
]

setup(
    name='pyrich',
    version=VERSION,
    author='Choi Ji Woo',
    author_email='cho2.jiwoo@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=install_requires,
    license='MIT',
    project_urls=project_urls,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={'console_scripts': ['pyrich=pyrich.control:run']},
)
