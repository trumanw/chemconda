from setuptools import setup, find_packages
from chemconda import __version__

install_requires = [
  'requests',
  'Click',
  'rich',
  'PyYAML',
]

setup(
  name = 'chemconda',
  packages=find_packages(),
  version = __version__,
  license='MIT',
  description = 'Install Conda and add ipykernel easily on Jupyter Notebook/Lab.',
  author = 'Truman Wu',
  author_email = 'chunan.woo@gmail.com',
  url = 'https://github.com/trumanw/chemconda',
  keywords = ['conda', 'miniconda', 'jupyter', 'ipykernel', 'AI', 'chemistry'],
  install_requires=install_requires,
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
  entry_points='''
    [console_scripts]
    chemconda=chemconda.cli:cli
  '''
)