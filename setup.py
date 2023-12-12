from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='finviz-data',
    version='v0.0.5',
    description='Simple package to get data from finviz.com',
    author='Dennis Iversen',
    author_email='dennis.iversen@gmail.com@com',
    url='https://github.com/diversen/finviz-data',  # Optional
    packages=find_packages(),
    install_requires=required,
    entry_points={
        'console_scripts': [
            # No scripts yet
            # 'finviz-data=finviz_data.main:main',
        ],
    },
)
