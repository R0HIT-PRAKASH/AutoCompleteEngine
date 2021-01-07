from __future__ import annotations
from typing import Any, List, Optional, Tuple
from prefix_tree import SimplePrefixTree

if self.value == prefix:
    new = SimplePrefixTree('sum')
    new.value = value
    self.subtrees.append(new)
else:
    new = SimplePrefixTree('sum')
    new_prefix = self.value + [prefix[len(self.value)]]
    for subtree in self.subtrees:
        if new_prefix == subtree.value:
            subtree.insert(value, weight, prefix)
    self.subtrees.append(new)
    new.value = new_prefix
    new.insert(value, weight, prefix)










if not self.is_leaf:
    if len(self.subtrees) > 1:
        for subtree in self.subtrees[1:]:
            lst = [self.subtrees[0]]
            counter = 0
            for item in lst:
                if subtree.weight >= item.weight:
                    lst.insert(counter, subtree)
                    counter += 1
                else:
                    lst.append(subtree)
                    counter += 1
            subtree.order_weight()
        self.subtrees = lst









