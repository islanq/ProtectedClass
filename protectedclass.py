from abc import ABC
from uuid import UUID
from datetime import datetime
from typing import Any


class DunderAttributeError(Exception):
    """Exception for when there are already a dunder in front of the attribute name"""


def is_dunder_prefix(string: str) -> bool:
    return string.startswith('__')


def is_dunder_suffix(string: str) -> bool:
    return string.endswith('__')


def is_dunder_attrib(string: str) -> bool:
    return is_dunder_prefix(string) and is_dunder_suffix(string)


def make_protected_name_prefix(name: str, ignore: bool = False) -> str:
    if ignore and len(name) > 2:
        if name.startswith('__'):
            raise DunderAttributeError
    return f'_{name}'


def undo_protected_name_prefix(name: str):
    if name.startswith('_'):
        return name.removeprefix('_')
    return name


def is_protected_name_prefix(name: str):
    return name.startswith('_')


class ProtectedClass(ABC):

    def __init__(self, *args, **kwargs) -> None:
        for arg in args:
            self._initprotect(arg, None)
        for k, v in kwargs.items():
            self._initprotect(k, v)

    def __setattr__(self, attr: str | int, value: Any) -> None:
        """
        :param attr: name of attribute
        :param value: value to associate
        """
        self.__dict__[f'{attr}'] = value

    def __delattr__(self, *attr):
        """
        :param attr: name or names of attributes to delete
        """
        for key in attr:
            if self._isforbidden(key):
                print(f'__delattr__("{key}"): WARNING: Unable to delete key')
            else:
                try:
                    del self.__dict__[key]
                except Exception as e:
                    print('Something went wrong with __delattr__: ', e, f'{key=}')

    def __getattr__(self, attr: str | int) -> Any:
        """
        __getattr__ is only called when __getattribute__ cannot
        find the attribute we are looking for.
        :param attr: attribute to look for
        :return: value at the location of the specific attribute
        """
        try:
            if attr in self.__dict__:
                return self.__dict__[attr]
            else:
                return self.__dict__[f'_{attr}']
        except KeyError:
            self.__setattr__(attr, None)
        return None

    def _initprotect(self, attr: str | int, value: Any) -> None:
        """
        this will place the _ {underscore} in front of the variable
        name for the dictionary upon initialization.

        If you wish to make additional attributes protected, you must
        use the protect or unprotect methods later.

        :param attr: key
        :param value: value
        """
        self.__setattr__(f'_{attr}', value)

    def _hasattr(self, attr) -> Any:
        """
        This is the internal has attribute method. Calling the hasattr()
        will NOT yield the right results to manage the interal workings of
        the protected data members. Although, it is still a completely
        valid operation for this class outside interal use.
        """
        return attr in self.__dict__

    def _hasprotectedattr(self, attr: object) -> bool:
        """
        :param attr: name of attribute
        :return: True if the attr is protected
        """
        if attr.startswith('_') and self._hasattr(attr):
            return True
        else:
            stripped = attr.lstrip('_').rstrip('_')
            if self._hasattr(f'_{stripped}'):
                return True
            if self._hasattr(f'__{stripped}'):
                return True
        return False

    def _hasunprotectedattr(self, attr):
        """
        :param attr: name of attribute
        :return: True if the attr is unprotected
        """
        stripped = attr.lstrip('_').rstrip('_')
        return self._hasattr(stripped)

    def _updateattr(self, oldname, newname):
        try:
            data = self.__getattr__(oldname)
            self.__setattr__(newname, data)
            self.__delattr__(oldname)
        except Exception as exception:
            print(f'_updateattr("{oldname=}, {newname=}"): Exception: {exception}')
            raise exception

    def _getforbiddenlist(self) -> list[str]:
        """
        Attempts to generate a list of what are believed to attributes
        with @property decorators. This is still in testing but seems to
        work okay with my limited use cases
        :return: a list of forbidden properties
        """
        inst = set(dir(self))
        clss = set(dir(type(self)))
        common = list(inst.intersection(clss))
        return [name for name in common
                if not callable(getattr(type(self), name))
                and not is_dunder_attrib(name)]

    def _isforbidden(self, attr) -> bool:
        """
        determines if the attribute is forbidden protection state change
        :param attr: attribute name
        :return: True if the attribute has a @property decorator
        """
        return attr.lstrip('_').rstrip('_') in self._getforbiddenlist()

    def protect(self, *attr):
        """
        protects attribute members
        :param attr: list of attributes to protect
        """
        keys = self.__dict__.copy().keys()
        attr = [*attr] if attr else keys

        for arg in attr:
            if (not self._isforbidden(arg)
                    and self._hasunprotectedattr(arg)):
                try:
                    old = undo_protected_name_prefix(arg)
                    new = make_protected_name_prefix(old)
                    self._updateattr(old, new)
                except Exception as e:
                    print('Something went wrong', e)

    def unprotect(self, *attr):
        """
        will unprotect member attributes by the name(s) specific.
        {default} if no names are specific, it will unprotect all attributes
        :param attr: list of attributes to unprotect
        """
        keys = self.__dict__.copy().keys()
        attr = [*attr] if attr else keys

        for arg in attr:
            if (not self._isforbidden(arg)
                    and self._hasprotectedattr(arg)):

                try:
                    old = make_protected_name_prefix(arg)
                    new = undo_protected_name_prefix(old)
                    self._updateattr(old, new)
                except Exception as e:
                    print('Something went wrong', e)


class MyDataClass(ProtectedClass):
    count: int
    backup_set: UUID
    backup_date: datetime
    type: str

    def __init__(self, *args, **kwargs):
        super().__init__('hello', *args, **kwargs)

    @property
    def backup_set(self):
        return UUID(self._backup_set)

    @property
    def backup_date(self):
        return datetime.fromtimestamp(float(self._backup_date) / 1000.00)

    @property
    def count(self):
        return int(self._count)


if __name__ == '__main__':
    data = {
        'count': '162',
        'backup_set': '76144912-5d67-4a6a-9f7d-3631bc901ad8',
        'backup_date': '1651039155045',
        'type': 'full'
    }

    backup = MyDataClass(**data)
    print(backup.__dict__)
    backup.unprotect('type')
    print(backup.__dict__)
    backup.protect('type')
    print(backup.__dict__)
