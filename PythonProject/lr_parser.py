#    CompilerFramework Python Version - LexerFramework
#    Copyright(C) 2023  刘迅承

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.If not, see<https://www.gnu.org/licenses/>.

from typing import Callable, Any, List, Tuple

from parser_framework import ParserFramework, ParseUnit, Production, ProductSentenceException
from bu_parser_framework import ConflictType, LRParserFramework, LRkItem, Closure


class LR_0_Parser(LRParserFramework):
    """
    The LR(0) Parser base on LRParserFramework

    Parameters
    ----------
    self.acc : bool
        is or not reached ACC after parsing
    """

    def __init__(self) -> None:
        super().__init__(0)
        self._conflict_log = ""

    def add_production_by_str_with_priority(self, product_sentence: str, priority: int = 0):
        """
        indirect way of add production by string, format string `product_sentence` as:
        `Pre ->|:|| Suf0 Suf1 ... [@SemantCallbackName[$priority='int']]`

        like this:
        `E -> F G` and set `priority`

        or like this:
        `E -> E add E @SemantAdd` and set `priority`

        or like this:
        `E | E opt E @SementOpt` and set `priority`

        or like this:
        `E : Delimiter E Delimiter @Semant` and set `priority`

        or with attr in string (attr will be string type), just add `$attr` directly behand `@SemantDelegateName`:
        `E -> E F @Semant$priority=0` and `$priority=0` will override priority in parameters. Larger number has higher priority. The min priority is 0.

        If you need Semant Callback, please add `semant_callback` use `add_semant_callback_dict` first.

        Parameters
        ----------
        product_sentence : str
            formated string
        priority : int, optional
            if production without priority, this priority will append in attr. Larger number has higher priority. The min priority is 0.

        Raises
        ------
        ProductSentenceException
            if `product_sentence` is illeagal
        """
        vs = product_sentence.split(" ")
        if vs[1] != "->" and vs[1] != "|" and vs[1] != ":":
            raise ProductSentenceException(product_sentence)
        last_index = len(vs) - 1
        semant_callback = self.none_semant_callback
        attr = {}
        if vs[last_index][0] == '@':
            s = vs[last_index][1:].split("$", 2)
            semant_callback = self.semant_callback_dict[s[0]]
            if len(s) == 2:
                if s[1]:
                    attr_s = s[1].split("&")
                    for attr_i in attr_s:
                        attr_i_s = attr_i.split("=")
                        if len(attr_i_s) > 1:
                            attr[attr_i_s[0]] = attr_i_s[1]
                        else:
                            attr[attr_i_s[0]] = None
            last_index -= 1
        sufs = vs[2:last_index + 1]
        if priority not in attr:
            attr['priority'] = priority
        production = Production(vs[0], sufs, semant_callback, attr)
        self.add_production(production)

    def read_conflict_log(self) -> str:
        return self._conflict_log

    def build_table(self,
                    augmented_grammar_semant_callback: Callable[[
                        List[ParseUnit]], Any] = ParserFramework.none_semant_callback,
                    augmented_grammar_attr: Any = None
                    ) -> None:
        """
        Build the LR(0) table, this will invoke :obj:`super().build_table()` and use buildin conflict callback to deal with conflicts. Buildin conflict callback will choose the first reduce item and return. (This means there are no real conflit deal.)

        Parameters
        ----------
        augmented_grammar_semant_callback : :obj:`Callable[[List[ParseUnit]], Any]`, optional
            the semant callback for new production in augmented grammar in :obj:`add_augmented_grammar()`
        augmented_grammar_attr : optional
            the attr for new production in augmented grammar in :obj:`add_augmented_grammar()`
        """
        def conflict_callback(ct: ConflictType, reduce_items: List[LRkItem], core_items: List[LRkItem]) -> Tuple[Closure.AddExtendReturn, List[LRkItem], List[LRkItem]]:
            # Write the condition in log
            if ct == ConflictType.MultiReduce:
                self._conflict_log += "Reduce-Reduce Conflict:\n"
            else:
                self._conflict_log += "Shift-Reduce Conflict:\n"
            if core_items:
                self._conflict_log += "Core Item(s):\n"
                for core_item in core_items:
                    self._conflict_log += core_item.print() + "\n"
            if reduce_items:
                self._conflict_log += "Reduce Production(s):\n"
                for reduce_item in reduce_items:
                    self._conflict_log += reduce_item.print(False) + "\n"
            # deal with conflit with priority
            max_priority = 0
            if core_items:
                return_item = core_items[0]
                is_r = False
            else:
                return_item = reduce_items[0]
                is_r = True
            for item in core_items:
                priority = 0
                if 'priority' in item.production.attr:
                    priority = int(item.production.attr['priority'])
                if priority > max_priority:
                    max_priority = priority
                    return_item = item
                    is_r = False
            for item in reduce_items:
                priority = 0
                if 'priority' in item.production.attr:
                    priority = int(item.production.attr['priority'])
                if priority > max_priority:
                    max_priority = priority
                    return_item = item
                    is_r = True
            self._conflict_log += "Conflict Solving Result:\n"
            self._conflict_log += return_item.print(not is_r) + "\n\n"
            if is_r:
                return Closure.AddExtendReturn.REDUCE, [return_item], []
            else:
                return Closure.AddExtendReturn.ADD, [], [return_item]

        super().build_table(conflict_callback,
                            augmented_grammar_semant_callback, augmented_grammar_attr)


class LR_1_Parser(LR_0_Parser):
    """
    The LR(1) Parser base on LR_0_Parser -> LRParserFramework

    Parameters
    ----------
    self.acc : bool
        is or not reached ACC after parsing
    """

    def __init__(self) -> None:
        super().__init__()
        self.k = 1


class SLR_Parser(LR_0_Parser):
    """
    The SLR Parser base on LR_0_Parser -> LRParserFramework

    Parameters
    ----------
    self.acc : bool
        is or not reached ACC after parsing
    """

    def __init__(self) -> None:
        super().__init__()
        self.SLR = True
