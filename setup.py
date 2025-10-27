from setuptools import setup, find_packages

setup(
    name="ecrp",
    version="0.1.0",
    packages=find_packages(),
    package_dir={'': '.'},  # Look for packages in the current directory
    install_requires=[
        "Flask==2.3.3",
    ],
    author="ECRP Team",
    description="Enhanced Code Review Platform",
    python_requires=">=3.8",
)