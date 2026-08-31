from setuptools import setup, Extension

module = Extension("vuln_module", sources=["vuln_module.c"])

setup(
    name="VulnModule",
    version="1.0",
    description="Python C Extension for Lab 71",
    ext_modules=[module],
)
