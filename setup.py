import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="aws-elemental-python-client", # Replace with your own username
    version="1.0.0",
    author="Juan Augusto Santos de Paula",
    author_email="jotaugusto93@gmail.com",
    description="Python Client for manage AWS Elemental Appliances (Delta, Live, Conductor)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juanaugusto/aws-elemental-python-client.git",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)