from setuptools import setup

setup(
    name='labutil',
    version='0.1.0',
    packages=['labutil'],
    install_requires=[
        'Click',
        'platformdirs',
        'PyYAML',
        'pipenv'
    ],
    entry_points={
        'console_scripts': [
            'labutil = labutil.cli:labutil',
        ],
    },
)
