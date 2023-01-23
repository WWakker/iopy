import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

about = {}
with open("iopy/__about__.py") as f:
    exec(f.read(), about)

with open("iopy/requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="iopy",
    version=about['__version__'],
    author=about['__authors__'],
    author_email=about['__email__'],
    description=about['__about__'],
    url=about['__url__'],
    license='MIT',
    long_description=long_description,
    long_description_content_type="markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=False,
    package_data={},
)
