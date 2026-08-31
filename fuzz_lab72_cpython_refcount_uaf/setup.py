from setuptools import setup, Extension

module = Extension("refcount_module", sources=["refcount_module.c"])

setup(
    name="RefcountModule",
    version="1.0",
    description="Python C-API Refcount UAF Lab 72",
    ext_modules=[module],
)
