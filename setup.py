from setuptools import setup

setup(
    name='bustracker',
    version='0.1',
    description="A service for looking up our next bus time.",

    author="Mark Smith",
    author_email="mark.smith@practicalpoetry.co.uk",

    packages=['bustracker'],
    package_dir={'': 'src'},
    install_requires=[
        'Flask~=0.11',
        'kylie~=0.3',
        'click~=6.6',
        'requests~=2.12',
    ],

    entry_points={
        'console_scripts': [
            'bustracker=bustracker:main',
        ],
    },

)
