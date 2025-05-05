from setuptools import setup, find_packages

setup(
    name='mcp-servers',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'fastmcp',
        'pyppeteer'
    ],
    entry_points={
        'console_scripts': [
            'lynx-server=mcp_servers.lynx_server:main',  # Adding command for lynx server
            'chrome-server=mcp_servers.chrome:main',  # Adding command for lynx server
        ],
    },
    url='https://github.com/WillChangeThisLater/mcp-servers',
    author='Paul Wendt',
    author_email='paul.wendt@temple.edu',
    description='Package containing servers for running commands',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
