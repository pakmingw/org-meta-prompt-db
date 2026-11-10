from setuptools import setup, find_packages

setup(
    name="orgprompt",
    version="0.1.0",
    packages=find_packages(include=["orgprompt*"]),
    package_data={
        "orgprompt.db": ["schema.sql"],
    },
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "orgprompt=orgprompt.cli:cli",
        ],
    },
)
