import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hunter-pkg-trevordbabcock",
    version="0.4.0",
    author="Trevor Babcock",
    author_email="trevor.d.babcock@gmail.com",
    description="A virtual ant farm of sorts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trevordbabcock/hunter/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)