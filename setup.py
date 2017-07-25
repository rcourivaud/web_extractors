from pip.req import parse_requirements
from setuptools import setup
from setuptools.command.install import install as _install


class Install(_install):
    def run(self):
        _install.do_egg_install(self)
        import nltk
        nltk.download("all")


install_reqs = parse_requirements("requirements.txt", session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    cmdclass={'install': Install},
    name='web_extractors',
    version='0.1',
    packages=['gmc_extractors', 'web_extractors.archi',
              'web_extractors.tools', 'web_extractors.meta_extractors'],
    url='',
    license='',
    author='Raphaël Courivaud',
    author_email='r.courivaud@gmail.com',
    description='Python Package used to optimize web content extraction with distributed system based on RabbitMq '
                'Architecture',
    package_data={'agents': ['UserAgents.txt']},
    include_package_data=True,
    install_requires=reqs,
    setup_requires=['nltk']
)
