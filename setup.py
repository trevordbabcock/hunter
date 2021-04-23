import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hunter-tdb",
    version="1.1",
    author="Trevor Babcock",
    author_email="trevor.d.babcock@gmail.com",
    description="A virtual ant farm of sorts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trevordbabcock/hunter/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Games/Entertainment"
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'hunter = hunter_pkg.main:main',
        ],
    }
)