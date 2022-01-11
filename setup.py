from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read()
requirements = [x for x in requirements.split("\n") if x != ""]


setup(
    name="pad_configuration",
    version="0.0.1",
    description=("Public Analysis Database configuration repository"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MadAnalysis/pad_configuration",
    author="J.Y. Araz",
    author_email=("jack.araz@durham.ac.uk"),
    license="GPL-3.0",
    package_dir={"": "src"},
    install_requires=requirements,
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
