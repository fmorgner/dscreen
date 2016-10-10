from setuptools import setup

setup(
    name='dscreen',
    version='0.1.1',
    description='A DBus XScreenSaver connector',
    long_description='',
    url='https://github.com/fmorgner/dscreen',
    author='Felix Morgner',
    author_email='felix.morgner@gmail.com',
    license='BSD',
    packages=[
        'dscreen',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ],
    keywords='screensaver dbus',
    install_requires=[
        'dbus-python',
    ],
    entry_points={
        'console_scripts': [
            'dscreen = dscreen.__init__:daemonize'
        ]
    },
)
