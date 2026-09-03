from setuptools import setup, Extension

module = Extension('subinterpreter_target', sources=['subinterpreter_target.c'])

setup(name='subinterpreter_target',
      version='1.0',
      description='CPython subinterpreter target for fuzzing',
      ext_modules=[module])
