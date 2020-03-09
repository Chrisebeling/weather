from setuptools import find_packages, setup

with open('requirements.txt') as f: 
    requirements = f.readlines() 

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(name='weather',
      version='0.1.3',
      description='Contains functions used to import and manipulate weather data.',
      long_description=readme,
      author='Chris Ebeling',
      author_email='chris.ebeling.93@gmail.com',
      classifiers=['Developer Status::3 - Alpha',
                   'Programming Language :: Python :: 3.7',
                   'Environment :: Win32 (MS Windows)',
                   'License :: OSI Approved :: MIT License'],
      license=license,
      package_data={
                    '': ['*.conf'],
                    },
      include_package_data=True,
      packages=find_packages(),
      install_requires=requirements
      )