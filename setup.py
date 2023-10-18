from setuptools import setup

setup(
    name='labutil',
    version='0.1.3',
    packages=['labutil'],
    install_requires=[
        'Click',
        'platformdirs',
        'PyYAML',
        'pipenv',
        'pywin32; platform_system=="Windows"',
    ],
    entry_points={
        'console_scripts': [
            'labutil = labutil.cli:labutil',
        ],
    },
)
