from setuptools import setup

setup(
    name='kittylog',
    version='0.1',
    description='Food log for the kitties (Dos and Bindi)',
    # url='http://github.com/akjmicro/kittylog',
    author='Aaron Krister Johnson',
    author_email='akjmicro@gmail.com',
    license='MIT',
    packages=['kittylog'],
    zip_safe=False,
    install_requires=[
        "flask",
        "wtforms"
    ]
)
