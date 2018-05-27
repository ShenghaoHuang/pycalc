import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycalc",
    version="0.0.2",
    author="Alexey Karpenko",
    author_email="38530214+k-alexey@users.noreply.github.com",
    description="Pure-python command-line calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/k-alexey/pycalc.git",
    packages=("pycalc",),
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
            ['pycalc = pycalc:_main']
        },
)
