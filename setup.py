from setuptools import setup, find_packages

setup(
    name="quant-edge-screener",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "yfinance==0.2.40",
        "pandas==2.2.2",
        "numpy==1.26.4",
        "backtrader==1.9.78.123",
        "pyyaml==6.0.2",
    ],
    author="nrutseab",
    description="Multi-factor trading edge screener",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
)
