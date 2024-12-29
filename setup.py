from setuptools import setup, find_packages

setup(
    name="hunter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "rich",
        "requests",
        "pyperclip",
    ],
    entry_points={
        'console_scripts': [
            'hunter=hunter.main:main',
        ],
    },
    python_requires=">=3.8",
    author="Joe",
    description="A powerful tool for extracting and enhancing markdown content from web pages",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 