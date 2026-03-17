from setuptools import setup, find_packages

setup(
    name="ecocache",
    version="0.1.0",
    author="Srivatsa Kumar",
    description="Semantic caching for LLM APIs that reduces water and carbon footprint",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GanugapatiSaiSowmya/ecocache",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "sentence-transformers==2.7.0",
        "faiss-cpu==1.7.4",
        "numpy==1.26.4",
        "python-dotenv",
        "flask",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)