######## version 1
#import weakref
#
#class constclassproperty(object):
#    def __init__(self, fget):
#        self.fget = fget
#    def __get__(self, owner_self, owner_cls):
#        return self.fget(owner_cls)

######## version 2
#import inspect
#
#class ClassPropertyDescriptor(object):
#
#    def __init__(self, fget, fset=None):
#        self.fget = fget
#        self.fset = fset
#
#    def __get__(self, obj, klass=None):
#        if klass is None:
#            klass = type(obj)
#        return self.fget.__get__(obj, klass)()
#
##    def __set__(self, obj, value):
##        if not self.fset:
##            raise AttributeError("can't set attribute")
##        type_ = type(obj)
##        return self.fset.__get__(obj, type_)(value)
#    def __set__(self, obj, value):
#       if not self.fset:
#           raise AttributeError("can't set attribute")
#       if inspect.isclass(obj):
#           type_ = obj
#           obj = None
#           raise RuntimeError
#       else:
#           type_ = type(obj)
#       print(obj, type_)
#       return self.fset.__get__(obj, type_)(value)
#
#
#    def setter(self, func):
#        if not isinstance(func, (classmethod, staticmethod)):
#            func = classmethod(func)
#        self.fset = func
#        return self
#
#class ClassPropertyMetaClass(type):
#    def __setattr__(self, key, value):
#        print("DDDDDDDDDDDDDD")
#        raise RuntimeError
#        if key in self.__dict__:
#            obj = self.__dict__.get(key)
#        if obj and type(obj) is ClassPropertyDescriptor:
#            return obj.__set__(self, value)
#
#        return super(ClassPropertyMetaClass, self).__setattr__(key, value)
#
#
#def classproperty(func):
#    if not isinstance(func, (classmethod, staticmethod)):
#        func = classmethod(func)
#
#    return ClassPropertyDescriptor(func)
#

# TODO once the setter of a derived class is called, 
#      the attributes in the base class and the derived class are independent
### source https://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python/35640842#35640842
### Mikhail Gerasimov and Michael Reinhardt
class classproperty:
    """
    Same as property(), but passes obj.__class__ instead of obj to fget/fset/fdel.
    Original code for property emulation:
    https://docs.python.org/3.5/howto/descriptor.html#properties
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj.__class__)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj.__class__, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj.__class__)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


def classproperty_support(cls):
    """
    Class decorator to add metaclass to our class.
    Metaclass uses to add descriptors to class attributes, see:
    http://stackoverflow.com/a/26634248/1113207
    """
    # Use type(cls) to use metaclass of given class
    class Meta(type(cls)):
        pass

    for name, obj in vars(cls).items():
        if isinstance(obj, classproperty):
            setattr(Meta, name, property(obj.fget, obj.fset, obj.fdel))

    class Wrapper(cls, metaclass=Meta):
        pass
    return Wrapper

# examples
if __name__ == "__main__":
    @classproperty_support
    class Bar(object):
        _bar = 1
    
        @classproperty
        def bar(cls):
            return cls._bar * 2
    
        @bar.setter
        def bar(cls, value):
            cls._bar = value - 1

        @classmethod
        def print(cls):
            """if called by derived classes, it will print the child version"""
            print(cls.bar)

    @classproperty_support
    class Child(Bar):
        _bar = 2

        @classproperty
        def bar(cls):
            return cls._bar * 3
    
        @bar.setter
        def bar(cls, value):
            cls._bar = value - 2
    
    
    # @classproperty should act like regular class variable.
    # Asserts can be tested with it.
    # class Bar:
    #     bar = 1


    # test instance instantiation
    foo = Bar()
    assert foo.bar == 2
    
    baz = Bar()
    assert baz.bar == 2

    assert Bar.bar == 2
    
    # test static variable
    baz.bar = 5
    assert foo.bar == 8
    assert Bar.bar == 8
    
    # test setting variable on the class
    Bar.bar = 50
    assert baz.bar == 98
    assert foo.bar == 98

    # if the child setter not called, two 'bar' are shared
    c1 = Child()
    c2 = Child()

    c1.print()
    assert c1.bar == 147
    assert c2.bar == 147
    assert Child.bar == 147

    # once the child setter is called, two 'bar' are independent
    c1.bar = 50
    assert c1.bar == 144
    assert c2.bar == 144
    assert Child.bar == 144

    # child class does not effect base class
    print(Bar.bar, baz.bar, foo.bar)
    #assert Bar.bar == 96
    #assert baz.bar == 96
    #assert foo.bar == 96

    Bar.bar = 10
    # base class does not effect child class
    print(Bar.bar, baz.bar, foo.bar, Child.bar, c1.bar, c2.bar)

    @classproperty_support
    class Doo(object):
        _bar = [1,2]

        @classproperty
        def bar(cls):
            return cls._bar

    for i in Doo.bar:
        print(i)
    #Doo.bar = []
