from distutils.core import setup

setup(
    name='web_extractors',
    version='0.1',
    packages=['gmc_extractors', 'web_extractors.archi', 'web_extractors.tools'],
    url='',
    license='',
    author='Raphaël Courivaud',
    author_email='r.courivaud@gmail.com',
    description='Python Package used to optimize web content extraction with distributed system based on RabbitMq Architecture',
    package_data={'agents': ['UserAgents.txt']},
    include_package_data=True,
    install_requires=['requests_cache', "requests", "beautifulsoup4", "pika", "ftfy", "lxml"],
)
