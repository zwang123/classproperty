# classproperty

Provide two Python class decorators `classproperty` and `classproperty_support`

## Installation
Add `$(pwd)/..` to the environment variable `$PYTHONPATH`

## Usage
```python
from classproperty import *
@classproperty_support
class Bar(object):
    _bar = 1

    @classproperty
    def bar(cls):
        return cls._bar

    @bar.setter
    def bar(cls, value):
        cls._bar = value
```
Read classproperty.py for more examples and details

## TODO
* There are some unexpected results when the derived class has a static member 
  with the same name as its base class's static member

## Note

This is deprecated since Python 3.9 as `@classmethod` can now wrap other descriptors such as `@property`.
See the [documentation](https://docs.python.org/3/library/functions.html).
