from setuptools import setup, find_packages

setup(
    name="hyparse",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["pandas>=2.2.0", "pydantic>=2.0.0"],
    python_requires=">=3.9",
    author="John Golliher",
    author_email="jwgollihe@gmail.com",
    description="A package for parsing .hy3 swimming meet results files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jgolliher/hyparse",
)
