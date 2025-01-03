from setuptools import setup

setup(
    name='PoePT',
    version='0.2.4',
    description='Python package for interacting with the Quora POE chatbot',
    author='Saikyo0',
    author_email='',
    url='https://github.com/FlyingYanglu/PoePT',
    packages=['poept'],
    install_requires=[
        'selenium',
        'webdriver_manager',
        'SpeechRecognition',
        'requests',
        'zipp',
        'seleniumbase'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
