"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type:
        The way the aggregate weight of the values in a tree is calculated

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.subtrees = []
        self.weight = 0.0
        self.weight_type = weight_type

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""

        if self.is_empty():
            return 0
        elif self.is_leaf():
            return 1
        else:
            counter = 0
            for subtree in self.subtrees:
                counter += len(subtree)
            return counter

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
        weight > 0
        The given value is either:
        1) not in this Autocompleter
        2) was previously inserted with the SAME prefix sequence


        >>> tree = SimplePrefixTree('sum')
        >>> tree.insert('park', 40.0, [])
        >>> print(tree)
        [] (40.0)
         park (40.0)
        """
        new = SimplePrefixTree(self.weight_type)
        if prefix is []:
            new.value = value
            new.weight = weight
            self.subtrees.append(new)
        else:
            if self.is_leaf() and self.value == value:
                self.weight += weight
            elif self.value == prefix and len(self.subtrees) != 0:
                for subtree in self.subtrees:
                    if subtree.is_leaf and subtree.value == value:
                        subtree.weight += weight
                        self.weight += weight
                        break
            elif self.value == prefix and len(self.subtrees) == 0:
                new.value = value
                new.weight = weight
                self.subtrees.append(new)
            else:
                new_prefix = self.value + [prefix[len(self.value)]]
                inside = False
                for subtree in self.subtrees:
                    if new_prefix == subtree.value:
                        subtree.insert(value, weight, prefix)
                        inside = True
                if not inside:
                    self.subtrees.append(new)
                new.value = new_prefix
                new.insert(value, weight, prefix)
        if self.weight_type == 'sum':
            self.weight += new.weight
        else:
            leaves = self._num_leaves()
            leaves_weight = self._sum_leaves()
            self.weight = leaves_weight / leaves
        self.subtrees.sort(key=lambda x: x.weight, reverse=True)

    def _inserted(self, value: Any, weight: float, prefix: List) -> bool:
        if self.is_leaf():
            return self.value == value
        else:
            for subtree in self.subtrees:
                if subtree._inserted(value, weight, prefix) is True:
                    return True
            return False

    def _weighting(self) -> float:
        if self.is_leaf():
            return self.weight
        else:
            if self.weight_type == "sum":
                self.weight = 0
                for subtree in self.subtrees:
                    self.weight += subtree._weighting()
                return self.weight
            else:
                temp_weight = 0.0
                for subtree in self.subtrees:
                    temp_weight += subtree._weighting()
                    self.weight = temp_weight / self._num_leaves()
                return temp_weight

    def _order_weight(self) -> None:
        if not self.is_leaf():
            if len(self.subtrees) >= 1:
                lst = [self.subtrees[0]]
                for subtree in self.subtrees[1:]:
                    index = 0  # find what index the tree should be inserted
                    # and insert into lst after the "item" for loop
                    for item in lst:
                        if subtree.weight < item.weight:
                            index += 1
                    lst.insert(index, subtree)
                self.subtrees = lst

    def _num_leaves(self) -> float:
        if self.is_leaf():
            return 1.0
        else:
            counter = 0.0
            for subtree in self.subtrees:
                counter += subtree._num_leaves()
            return counter

    def _sum_leaves(self) -> float:
        if self.is_leaf():
            return self.weight
        else:
            counter = 0.0
            for subtree in self.subtrees:
                counter += subtree._sum_leaves()
            return counter

        # for subtree in self.subtrees:
        #     if subtree.is_leaf():
        #

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        s = self._str_indented()
        return s

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight}) \n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            if limit is None:
                lst = []
                if prefix == []:
                    for subtree in self.subtrees:
                        lst.extend(subtree.autocomplete(prefix, limit))
                        lst.sort(key=lambda tup: tup[1], reverse=True)
                    return lst
                else:
                    for subtree in self.subtrees:
                        if prefix[0:len(subtree.value)] == subtree.value:
                            if len(subtree.value) == len(prefix):
                                lst.extend(subtree.autocomplete([], limit))
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                            else:
                                lst.extend(subtree.autocomplete(prefix, limit))
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                    return lst
            else:
                lst = []
                if prefix == []:
                    for subtree in self.subtrees:
                        lst.extend(subtree.autocomplete(prefix, limit))
                        lst.sort(key=lambda tup: tup[1], reverse=True)
                        if len(lst) == limit:
                            return lst

                    return lst
                else:
                    for subtree in self.subtrees:
                        if prefix[0:len(subtree.value)] == subtree.value:
                            if len(subtree.value) == len(prefix):
                                lst.extend(subtree.autocomplete([], limit))
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                                if len(lst) == limit:
                                    return lst

                            else:
                                lst.extend(subtree.autocomplete(prefix, limit))
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                                if len(lst) == limit:
                                    return lst
                    if len(lst) > limit:
                        lst.__delitem__(len(lst) - 1)
                    return lst

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        if self.is_leaf():
            self.value = 0
            self.weight = 0
        elif prefix == []:
            for subtree in self.subtrees:
                if subtree.is_leaf():
                    self.weight -= subtree.weight
                subtree.remove([])
                subtree._weighting()
                self._weighting()
                subtree._clean()

        else:
            for subtree in self.subtrees:
                if prefix[0:len(subtree.value)] == subtree.value:
                    if subtree.value == prefix:
                        if subtree.is_leaf():
                            self.weight -= subtree.weight
                        subtree.remove([])
                        subtree._weighting()
                        self._weighting()
                        subtree._clean()
                    else:
                        if subtree.is_leaf():
                            self.weight -= subtree.weight
                        subtree.remove(prefix)
                        subtree._weighting()
                        self._weighting()
                        subtree._clean()
                    if subtree.weight == 0:
                        self.subtrees.remove(subtree)

    def _clean(self) -> None:
        for subtree in self.subtrees:
            if subtree._num_leaves() == 0:
                self.subtrees.remove(subtree)
            if subtree.is_empty() and subtree in self.subtrees:
                self.subtrees.remove(subtree)


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]

    def __init__(self, weight_type: str):
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
        weight > 0
        The given value is either:
        1) not in this Autocompleter
        2) was previously inserted with the SAME prefix sequence
        """
        new = CompressedPrefixTree(self.weight_type)

        if self.value == [] and len(self.subtrees) == 0:
            self.value = prefix
            new.value = value
            new.weight = weight
            self.subtrees.append(new)
            if self.weight_type == 'sum':
                self._summing()
            elif self.weight_type == 'average':
                self._aver()
        else:
            if prefix == self.value and not self.is_leaf():
                new.value = value
                new.weight = weight
                self.subtrees.append(new)
            else:
                if self.is_leaf() and self.value == value:
                    self.weight += weight
                # this is fine (^)
                elif self.value == prefix:
                    new.value = value
                    new.weight = weight
                    self.subtrees.append(new)
                # this is fine, although unnecessary? (^)

                else:
                    common = []
                    for subtree in self.subtrees:
                        common.append(len(subtree.longest_common(prefix)))
                    self._insertion(common, value, weight, prefix)

    def _insertion(self, common, value, weight, prefix) -> None:
        new = CompressedPrefixTree(self.weight_type)
        if sum(common) == 0:
            new_parent = CompressedPrefixTree(self.weight_type)
            new_parent.value = self.value
            new_parent.subtrees = self.subtrees
            self.value = []
            self.subtrees = []
            self.weight = 0.0
            self.subtrees.append(new_parent)
            new_insert = CompressedPrefixTree(self.weight_type)
            new_insert.value = prefix
            new.value = value
            new.weight = weight
            new_insert.subtrees.append(new)
            self.subtrees.append(new_insert)
            if self.weight_type == 'sum':
                new_insert._summing()
                new_parent._summing()
                self._summing()
            elif self.weight_type == 'average':
                new_insert._aver()
                new_parent._aver()
                self._aver()

        else:
            large = max(common)
            if large == 0:
                new.value = prefix
                obj = CompressedPrefixTree(self.weight_type)
                obj.value = value
                obj.weight = weight
                new.subtrees.append(obj)
                self.subtrees.append(new)
            else:
                subtree = self.subtrees[common.index(large)]
                if len(subtree.value) == large and not \
                        subtree.is_leaf():
                    subtree.insert(value, weight, prefix)
                elif len(subtree.value) == large and \
                        subtree.is_leaf():
                    new.value = prefix
                    new_child = CompressedPrefixTree(
                        self.weight_type)
                    new_child.value = value
                    new_child.weight = weight
                    new.subtrees.append(new_child)
                    self.subtrees.append(new)
                    if self.weight_type == 'sum':
                        new_child._summing()
                        new._summing()
                        self._summing()
                    elif self.weight_type == 'average':
                        new_child._aver()
                        new._aver()
                        self._aver()

                elif not subtree.is_leaf():
                    first_prefix = []
                    for i in range(large):
                        first_prefix.append(subtree.value[i])

                    new_parent = CompressedPrefixTree(
                        self.weight_type)
                    new_parent.value = subtree.value
                    subtree.value = first_prefix
                    new_parent.subtrees.extend(subtree.subtrees)
                    subtree.subtrees = [new_parent]
                    insert_parent = CompressedPrefixTree(
                        self.weight_type)
                    insert_parent.value = prefix
                    insert_child = CompressedPrefixTree(
                        self.weight_type)
                    insert_child.value = value
                    insert_child.weight = weight
                    insert_parent.subtrees.append(insert_child)
                    subtree.subtrees.append(insert_parent)
                    if self.weight_type == 'sum':
                        insert_parent.summing()
                        new_parent.summing()
                        subtree.summing()
                        self.summing()
                    elif self.weight_type == 'average':
                        insert_parent._aver()
                        new_parent._aver()
                        subtree._aver()
                        self._aver()
                    self.subtrees.sort(key=lambda x: x.weight,
                                       reverse=True)
                    subtree.subtrees.sort(key=lambda x: x.weight,
                                          reverse=True)
                    insert_parent.subtrees.sort(key=lambda
                        x: x.weight, reverse=True)
                    new_parent.subtrees.sort(key=lambda
                        x: x.weight, reverse=True)

                elif subtree.is_leaf():
                    first_prefix = []
                    for i in range(large):
                        first_prefix.append(subtree.value[i])
                    new_parent = CompressedPrefixTree(
                        self.weight_type)
                    new_parent.value = self.value
                    self.value = first_prefix
                    new_parent.subtrees.extend(self.subtrees)
                    self.subtrees = [new_parent]
                    insert_parent = CompressedPrefixTree(
                        self.weight_type)
                    insert_parent.value = prefix
                    insert_child = CompressedPrefixTree(
                        self.weight_type)
                    insert_child.value = value
                    insert_child.weight = weight
                    insert_parent.subtrees.append(insert_child)
                    self.subtrees.append(insert_parent)
                    if self.weight_type == 'sum':
                        insert_parent._summing()
                        new_parent._summing()
                        subtree._summing()
                        self._summing()
                    elif self.weight_type == 'average':
                        insert_parent._aver()
                        new_parent._aver()
                        subtree._aver()
                        self._aver()
                    self.subtrees.sort(key=lambda x: x.weight,
                                       reverse=True)
                    subtree.subtrees.sort(key=lambda x: x.weight,
                                          reverse=True)
                    insert_parent.subtrees.sort(key=lambda
                        x: x.weight, reverse=True)
                    new_parent.subtrees.sort(key=lambda
                        x: x.weight, reverse=True)

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None):
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            if limit is None:
                lst = []
                if prefix == []:
                    for subtree in self.subtrees:
                        lst.extend(subtree.autocomplete(prefix))
                        lst.sort(key=lambda tup: tup[1], reverse=True)
                    return lst
                else:
                    for subtree in self.subtrees:
                        if prefix[0:len(subtree.value)] == subtree.value:
                            if len(subtree.value) == len(prefix):
                                lst.extend(subtree.autocomplete([]))
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                            else:
                                lst.extend(subtree.autocomplete(prefix))
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                    return lst
            else:
                lst = []
                if prefix == []:
                    for subtree in self.subtrees:
                        result = (subtree.autocomplete([], limit))
                        for item in result:
                            if len(lst) + 1 == limit:
                                lst.extend(item)
                                lst.sort(key=lambda tup: tup[1],
                                         reverse=True)
                                break
                        lst.sort(key=lambda tup: tup[1], reverse=True)
                        if len(lst) == limit:
                            return lst

                    return lst
                else:
                    for subtree in self.subtrees:
                        if prefix[0:len(subtree.value)] == subtree.value:
                            if len(subtree.value) == len(prefix):
                                result = (subtree.autocomplete([], limit))
                                for item in result:
                                    if len(lst)+1 == limit:
                                        lst.extend(item)
                                        lst.sort(key=lambda tup: tup[1],
                                                 reverse=True)
                                        break
                                lst.sort(key=lambda tup: tup[1], reverse=True)
                                if len(lst) == limit:
                                    return lst

                            else:
                                result = (subtree.autocomplete([], limit))
                                for item in result:
                                    if len(lst)+1 == limit:
                                        lst.extend(item)
                                        lst.sort(key=lambda
                                            tup: tup[1], reverse=True)
                                        break

                            if len(lst) == limit:
                                    return lst
                    if len(lst) > limit:
                        lst.__delitem__(len(lst) - 1)
                    return lst




    # def _weighting(self) -> float:
    #     if self.weight_type == 'sum':
    #         self.weight = self._sum_leaves()
    #     else:
    #         leaves = self._num_leaves()
    #         leaves_weight = self._sum_leaves()
    #         self.weight = leaves_weight / leaves
    def _summing(self) -> float:
        if not self.is_leaf():
            self.weight = 0.0
            for subtree in self.subtrees:
                self.weight += subtree.weight
            return self.weight

    def _aver(self):
        if not self.is_leaf():
            self.weight = 0.0
            sum = self._summing()
            leaves = self._num_leaves()
            self.weight = sum/leaves

    def longest_common(self, other: Union[List, str]) -> List[Any]:
        counter = 0
        result = []
        if isinstance(other, str):
            oth = list(other)
        else:
            oth = other
        while counter < len(self.value) and counter < len(oth):
            if self.value[counter] == oth[counter]:
                result.append(self.value[counter])
                counter += 1
            else:
                break
        return result

# if __name__ == '__main__':
#     import python_ta
#     python_ta.check_all(config={
#         'max-nested-blocks': 4
#     })
