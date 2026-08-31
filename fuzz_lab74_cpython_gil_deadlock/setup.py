from setuptools import setup, Extension

module = Extension("gil_module", sources=["gil_module.c"])

setup(
    name="GilModule",
    version="1.0",
    description="Python C-API GIL Deadlock Lab 74",
    ext_modules=[module],
)
