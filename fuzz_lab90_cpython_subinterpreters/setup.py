from distutils.core import setup, Extension
import sysconfig

module = Extension('subinterpreter_target',
                   sources=['subinterpreter_target.c'],
                   include_dirs=[sysconfig.get_python_inc()])

setup(name='subinterpreter_target',
      version='1.0',
      description='CPython subinterpreter target for fuzzing',
      ext_modules=[module])
