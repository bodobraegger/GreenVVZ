import collections
from datetime import date
import re

# returns a dictionary containing the values 'year' and 'session' as of today
def current_session():
    if date.today() < date(date.today().year, 2, 1):
        return {'year': current_year() - 1, 'session': '003'}
    elif date.today() < date(date.today().year, 8, 1):
        return {'year': current_year() - 1, 'session': '004'}
    else:
        return {'year': current_year(), 'session': '003'}


# returns a dictionary containing the values 'year' and 'session' of the upcoming semester
def next_session():
    if date.today() < date(date.today().year, 2, 1):
        return {'year': current_year() - 1, 'session': '004'}
    elif date.today() < date(date.today().year, 8, 1):
        return {'year': current_year(), 'session': '003'}
    else:
        return {'year': current_year(), 'session': '004'}


# returns a dictionary containing the values 'year' and 'session' of the previous semester
def previous_session():
    if date.today() < date(date.today().year, 2, 1):
        return {'year': current_year() - 2, 'session': '004'}
    elif date.today() < date(date.today().year, 8, 1):
        return {'year': current_year() - 1, 'session': '003'}
    else:
        return {'year': current_year() - 1, 'session': '004'}


# returns current year as int
def current_year():
    return date.today().year

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

            
if __name__ == '__main__':
    s = OrderedSet('abracadaba')
    t = OrderedSet('simsalabim')
    print(s | t)
    print(s & t)
    print(s - t)