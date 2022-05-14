# ProtectedClass

A simple abstract class that allows you to dump in arbitrary amount of data upon initialization which will set all your internal attributes to private (e.g. instance._attrib)

# Motivation
I had an extensive set of xml data I was reading in from string. The xml.etree.ElementTree.fromstring(...) is extremely fast, however, the dictionary object it renders is always a plain old dictionary; all keys and values read as a string. However, some class object(s) I was reading in were sometimes HUNDREDS of key value pairs. Similarly, I didn't know what data I would ultimately use, as I could see there was obviously some I wouldn't be interested in, but had it nonetheless.

With that said, I like type hints, I like data types other than string, but I'm lazy... I feel this meets the sweet spot...

```
class MyClass(ProctectedClass):
    date: datetime
    contact_name: str
    message_id: int
    ...

    def __init(self, *args, **kwargs):
        super().__init(*args, **kwargs)
```
Next we simply write the properties that interest us and adorn them with the ``@property`` decorator (for example)

```
    @property
    def date(self):
        return datetime(self._date)
        
    @property
    def message_id(self):
        return int(self._message_id)
```

# What did we gain?
1) We didn't have to init everything ourselves with our self._data = data
2) We didn't have to decide how to extract the data type in the init
3) We can now simply grab and set the data type with our property.getter methods
4) Our type hints are cluttered with all the ugly mangled names.
5) We simply add more getter properties as our needs grow or other data members become a concern.

# Finally...
I have only been coding in python a few weeks, but I wanted to mess around with the dunder methods ``__getattr__`` ``__getattribute__`` ``__setattr__``, etc... So, if there is something out there that does this already, and if there is, I would image a 100x better, no worries! It was still a fun exercise and I learned a lot while working on this. I hope someone can get some use out of it or improve it. 
