from setuptools import setup, Extension

module = Extension("pymalloc_module", sources=["pymalloc_module.c"])

setup(
    name="PymallocModule",
    version="1.0",
    description="CPython pymalloc Boundary Lab 82",
    ext_modules=[module],
)
