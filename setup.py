"""qureed installation configuration"""

import os

from setuptools import find_packages, setup

current_dir = os.path.abspath(os.path.dirname(__file__))
setup(
    name="qureed_gui",
    version="0.0.1",
    author="Simon Sekavčnik",
    author_email="simon.sekavcnik@tum.de",
    description="QuReed Grafical Interface",
    license="Apache 2.0",
    packages=find_packages(where="."),
    install_requires=[
        "flet==0.27.6",
        "flet-desktop==0.27.6",
        "rapidfuzz",
        "toml",
        "click",
        "qureed-project-server @ git+ssh://git@github.com/tqsd/QuReedGuiServer.git@master",
        "qureed @ git+ssh://git@github.com/tqsd/QuReed.git@standardization",
    ],
    package_data={
        "qureed_gui":[" wheels/**/*.whl"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "qureed_debug=qureed_gui.main:run",
            "qureed=qureed_gui.app:cli"
        ]
    },
)
