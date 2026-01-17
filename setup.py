from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, Extension
try:
    import pybind11
    pybind11_available = True
except ImportError:
    pybind11_available = False

if pybind11_available:
    include_dirs = [pybind11.get_include()]
else:
    include_dirs = []

ext_modules = [
    Pybind11Extension(
        "fast_greeks",
        [
            "backend/cpp_engine/greeks.cpp",
        ],
        include_dirs=include_dirs,
        language='c++',
        cxx_std=17,
    ),
]

setup(
    name="theta-prime",
    version="0.1.0",
    author="Theta-Prime Team",
    description="High-performance options analytics platform with C++ backend",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    setup_requires=["pybind11>=2.10.0"],
    install_requires=[
        "pybind11>=2.10.0",
    ],
)

