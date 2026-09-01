from setuptools import setup, Extension

module = Extension("nogil_module", sources=["nogil_module.c"])

setup(
    name="NogilModule",
    version="1.0",
    description="Cython nogil Race Target Lab 80",
    ext_modules=[module],
)
