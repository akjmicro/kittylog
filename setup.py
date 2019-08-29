from setuptools import setup

setup(
    name='kittylog',
    version='1.0',
    description='Food log for the kitties',
    url='http://github.com/akjmicro/kittylog',
    author='Aaron Krister Johnson',
    author_email='akjmicro@gmail.com',
    license='MIT',
    packages=['kittylog'],
    zip_safe=False,
    install_requires=[
        "pyyaml",
        "flask",
        "wtforms",
        "gunicorn"
    ]
)
