from setuptools import setup, find_packages

setup(
    name="pychocolate",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "chocolate=chocolate.__main__:main",
        ],
    },
    author="Chocolateisfr",
    description="A project manager CLI tool.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/frchocolate/chocolate",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
