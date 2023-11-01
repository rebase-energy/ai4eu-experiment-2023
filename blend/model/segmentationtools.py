from itertools import combinations

# https://stackoverflow.com/questions/45820190/set-ordered-partitions-in-python-of-maximum-size-n
def segmentations(iterable, k):
    """
    Yield the set partitions of *iterable* into *k* parts. Set partitions are
    order-preserving.

    >>> iterable = 'abc'
    >>> for part in segmentations(iterable, 2):
    ...     print([''.join(p) for p in part])
    ['a', 'bc']
    ['ab', 'c']
    
    """
    
    n = len(iterable)
    assert 1 <= k <= n, (n, k)

    def split_at(js):
        i = 0

        for j in js:
            yield iterable[i:j]
            i = j

        yield iterable[i:]

    for separations in combinations(range(1, n), k - 1):
        yield list(split_at(separations))


# https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/more.html#set_partitions
def set_partitions(iterable, k=None):
    """
    Yield the set partitions of *iterable* into *k* parts. Set partitions are
    not order-preserving.

    >>> iterable = 'abc'
    >>> for part in set_partitions(iterable, 2):
    ...     print([''.join(p) for p in part])
    ['a', 'bc']
    ['ab', 'c']
    ['b', 'ac']


    If *k* is not given, every set partition is generated.

    >>> iterable = 'abc'
    >>> for part in set_partitions(iterable):
    ...     print([''.join(p) for p in part])
    ['abc']
    ['a', 'bc']
    ['ab', 'c']
    ['b', 'ac']
    ['a', 'b', 'c']

    """
    L = list(iterable)
    n = len(L)
    if k is not None:
        if k < 1:
            raise ValueError(
                "Can't partition in a negative or zero number of groups"
            )
        elif k > n:
            return

    def set_partitions_helper(L, k):
        n = len(L)
        if k == 1:
            yield [L]
        elif n == k:
            yield [[s] for s in L]
        else:
            e, *M = L
            for p in set_partitions_helper(M, k - 1):
                yield [[e], *p]
            for p in set_partitions_helper(M, k):
                for i in range(len(p)):
                    yield p[:i] + [[e] + p[i]] + p[i + 1 :]

    if k is None:
        for k in range(1, n + 1):
            yield from set_partitions_helper(L, k)
    else:
        yield from set_partitions_helper(L, k)
