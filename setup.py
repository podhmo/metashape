from setuptools import setup, find_packages

tests_requires = ["pytest"]

setup(
    classifiers=[
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">3.5",
    packages=find_packages(exclude=["metashape.tests"]),
    install_requires=[
        "typing_inspect",
        "typing_extensions",
        "magicalimport",
        "dictknife",
    ],
    extras_require={
        "testing": tests_requires,
        "dev": ["black", "flake8"] + tests_requires,
        "input": ["json2python-models"],  # todo: omit
    },
    tests_require=tests_requires,
    test_suite="metashape.tests",
)
