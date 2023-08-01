# RedOnly
[![tests](https://github.com/cnovel/redonly/actions/workflows/python-test.yml/badge.svg)](https://github.com/cnovel/redonly/actions/workflows/python-test.yml)
[![codecov](https://codecov.io/gh/cnovel/redonly/branch/main/graph/badge.svg?token=nZ6KVUwGel)](https://codecov.io/gh/cnovel/redonly)
![PyPI](https://img.shields.io/pypi/v/redonly)

`redonly` is a Python package used for creating a static archive of Reddit subs at present time.

The goal of *RedOnly* is to prevent doomscrolling and comment-reading only on Reddit.

![Screen capture of RedOnly](img/screencap.png)

## How to use
Here's a minimal example for using RedOnly:
```python
import redonly.redonly as ro


ronly = ro.RedOnly("output_folder", ["france", "europe", "ProgrammerHumor"])
if not ronly.generate():
    print("Failed to generate!")
else:
    print("Success")
```
