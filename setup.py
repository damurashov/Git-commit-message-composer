from setuptools import setup

def get_long_description():
    with open("README.md", 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="gico",
    packages=[
        "gico"
    ],
    include_package_data=True,
    license="MIT",
    description="Gico makes your git history consistent, and your changes -- traceable",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/damurashov/TIRED",
    author="Dmitry Murashov",
    setup_requires=["wheel"],
    install_requires=[
        "tired @ git+https://github.com/damurashov/TIRED.git@master",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    version="1.0.7",
    entry_points="""
        [console_scripts]
        gico = gico.gico:main
    """
)

