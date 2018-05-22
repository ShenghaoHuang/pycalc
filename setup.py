import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycalc",
    version="0.0.1",
    author="Alexey Karpenko",
    author_email="alexeyp750@gmail.com",
    description="Pure-python command-line calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Office/Business",
    ),
    entry_points={
        'console_scripts':
            ['pycalc = pycalc.pycalc:main']
        },
)
