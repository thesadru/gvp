from setuptools import setup

setup(
    name="gvp",
    version="1.1",
    author="thesadru",
    packages=["gvp"],
    description="An api wrapper for Gymnázium na Vítězné pláni",
    keywords="api wrapper".split(),
    python_requires=">=3.7",
    url="https://github.com/thesadru/gvp",
    install_requires=["requests", "bs4"],
    author_email="thesadru@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
