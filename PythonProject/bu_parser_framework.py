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

from enum import Enum
from typing import Callable, Any, List, Tuple, Dict
import time
from queue import LifoQueue

from lexer_framework import LexerResult
from parser_framework import ParserFramework, Production, ParseUnit


def add_augmented_grammar(productions: List[Production], semant_callback: Callable[[List[ParseUnit]], Any] = ParserFramework.none_semant_callback, attr: Any = None) -> List[Production]:
    """
    Add augmented grammar for the first production and return new `productions`, the new 'S' is named "@S".

    Parameters
    ----------
    productions : :obj:`list` of :obj:`Production`
        the productions
    semant_callback : :obj:`Callable` of :obj:`list` of :obj:`ParseUnit` with return :obj:`Any`, optional
        the callback when reduce one production for semant analysis
    attr : :obj:`Any`, optional
        attr for advansing usage

    Returns
    -------
    :obj:`list` of :obj:`Production`
        new `productions` that are added augmented grammar
    """
    aug_production = Production(
        "@S", [productions[0].pre], semant_callback, attr)
    return [aug_production] + productions


class LRkItem:
    """
    LR(k) Item class
    """

    def __init__(self, production: Production, dot_pos: int = 0, follow: List[str] = []) -> None:
        """
        LR(k) Item class

        Parameters
        ----------
        production : :obj:`Production`
            the production of this LR Item
        dot_pos : int, optional
            the dot '•' position in this item
        follow : :obj:`list` of str, optional
            the follow, number is k
        """
        self.production = production
        self.dot_pos = dot_pos
        self.follow = follow

    def add(self, symbol: str) -> bool:
        """
        Add a symbol and if this symbol can be adopted, then move the dot '•' forward, if not, do nothing.

        Parameters
        ----------
        symbol : str
            the symbol added

        Returns
        -------
        bool
            move the dot '•' forward or not
        """
        if self.dot_pos < 0 or self.dot_pos >= len(self.production.sufs):
            return False
        if self.production.sufs[self.dot_pos] == symbol:
            self.dot_pos += 1
            return True
        else:
            return False

    def is_on_reduce(self, symbol: str) -> bool:
        """
        Return `True` if the dot '•' at the tail of this product, and can be reduce.

        Parameters
        ----------
        symbol : str
            the symbol added

        Returns
        -------
        bool
            can be reduce or not
        """
        if self.dot_pos >= len(self.production.sufs):
            if self.follow:  # LR(1)
                if self.follow[0] == symbol:
                    return True
                else:
                    return False
            else:  # LR(0)
                return True
        else:
            return False

    def set_follow(self, follow: List[str] = []) -> None:
        """
        set a new follow.

        Parameters
        ----------
        follow : :obj:`list` of str, optional
            the follow, number is k
        """
        self.follow = follow

    def deep_copy(self):
        """
        Deep copy self
        """
        return LRkItem(self.production.deep_copy(), self.dot_pos, [i for i in self.follow])


class Closure:
    """
    Closure of LR item sets, including LR(0) and LR(1)

    Parameters
    ----------
    self.k : int
        0 or 1, LR(0) or LR(1)
    self.recieved_productions : :obj:`list` of :obj:`Production`
        productions accepted to closure by core production in `__init__`
    self.symbol_LR_item_dict : :obj:`Dict[str, List[LRkItem]]`
        by product.pre to find LRkItems
    self.terminals : :obj:`list` of str
        the terminals in `self.recieved_productions`
    self.nonterminals : :obj:`list` of str
        the nonterminals in `self.recieved_productions`
    self.first_dict : :obj:`Dict[str, List[str]]`
        For LR(1), the first set for each nonterminal
    self.follow_dict : :obj:`Dict[str, List[str]]`
        For LR(1), the follow set for each nonterminal
    """

    def __init__(self, productions: List[Production], k: int = 0) -> None:
        """
        Closure of LR item sets, including LR(0) and LR(1), core production is the first product in `productions`

        Parameters
        ----------
        productions : :obj:`list` of :obj:`Production`
            productions to calc `Closure`
        k : int, optional
            LR(k), now support 0 and 1, default 0
        """
        self.terminals: List[str] = []
        self.nonterminals: List[str] = []
        self.k = k
        if not productions:
            return
        # check all production
        check_list = []
        check_symbol = [productions[0].pre]
        list_len = -1
        while len(check_list) != list_len:
            list_len = len(check_list)
            for i in range(len(productions)):
                production = productions[i]
                if production.pre in check_symbol and i not in check_list:
                    check_symbol += production.sufs
                    check_symbol = list(set(check_symbol))
                    check_list.append(i)
        self.recieved_productions: List[Production] = []
        for i in check_list:
            self.recieved_productions.append(productions[i])
        # collect productions into dict for find
        self.symbol_LR_item_dict: Dict[str, List[LRkItem]] = {}
        for production in self.recieved_productions:
            LR_item = LRkItem(production)
            if production.pre not in self.symbol_LR_item_dict:
                self.symbol_LR_item_dict[production.pre] = [LR_item]
            else:
                self.symbol_LR_item_dict[production.pre].append(LR_item)
        # split terminal and nonterminal
        for symbol in check_symbol:
            if symbol in self.symbol_LR_item_dict:
                self.nonterminals.append(symbol)
            else:
                self.terminals.append(symbol)

        # LR(0) is ok, next is for LR(1)

        self.first_dict: Dict[str, List[str]] = {}

        def find_first(self, first: str):
            # terminal is first
            if first in self.terminals:
                return [first]
            # searched first
            if first in self.first_dict:
                return self.first_dict[first]
            # nonterminal and unsearched, do it.
            first_list = []
            for LR_item in self.symbol_LR_item_dict[first]:
                first = LR_item.production.sufs[0]
                # next recurrence
                first_list += find_first(self, first)
            # add search result
            self.first_dict[first] = first_list
            # return to upper recurrence
            return first_list

        self.follow_dict: Dict[str, List[str]] = {}

        if k == 1:
            # calc FIRST set
            for nonterminal in self.nonterminals:
                find_first(self, nonterminal)
            # calc FOLLOW set
            for nonterminal in self.nonterminals:
                self.follow_dict[nonterminal] = ['@EOF']
            for nonterminal in self.nonterminals:
                for LR_item in self.symbol_LR_item_dict[nonterminal]:
                    if len(LR_item.production.sufs) < 2:
                        continue
                    for symbol, follow_symbol in zip(LR_item.production.sufs[:-1], LR_item.production.sufs[1:]):
                        if symbol in self.nonterminals:
                            if follow_symbol in self.terminals:
                                self.follow_dict[symbol].append(follow_symbol)
                            else:
                                self.follow_dict[symbol] += self.first_dict[follow_symbol]
            # add lookahead terminals
            temp_symbol_LR_item_dict = {}
            for nonterminal in self.nonterminals:
                LR_items = []
                for LR_item in self.symbol_LR_item_dict[nonterminal]:
                    for follow in set(self.follow_dict[nonterminal]):
                        LR_item.set_follow([follow])
                        LR_items.append(LR_item)
                temp_symbol_LR_item_dict[nonterminal] = LR_items
            self.symbol_LR_item_dict = temp_symbol_LR_item_dict

    def deep_copy(self):
        """
        Deep copy self.
        """
        temp = Closure([], self.k)
        temp.recieved_productions = [p.deep_copy()
                                     for p in self.recieved_productions]
        for nonterminal in self.nonterminals:
            temp.symbol_LR_item_dict[nonterminal] = [
                item.deep_copy() for item in self.symbol_LR_item_dict[nonterminal]]
        temp.terminals = [i for i in self.terminals]
        temp.nonterminals = [i for i in self.nonterminals]
        for nonterminal in self.nonterminals:
            temp.first_dict[nonterminal] = [
                i for i in self.first_dict[nonterminal]]
            temp.follow_dict[nonterminal] = [
                i for i in self.follow_dict[nonterminal]]
        return temp

    AddExtendReturn = Enum("AddExtendReturn", "NONE REDUCE ADD CONFLICT")

    def add_and_extend(self, symbol: str) -> Tuple[AddExtendReturn, List[LRkItem], List[LRkItem]]:
        """
        For build LR Table, add a symbol to closure and extend this closure. Suggest deep copy this closure for backup first. If goto-reduce conflit detected, still do goto change for this closure, and return the reduce items too. You can keep the changed closure for 'goto' or not keep closure but keep reduce items for 'reduce'.

        Parameters
        ----------
        symbol : str
            the added symbol or incur reduce

        Returns
        -------
        :obj:`Tuple[AddExtendReturn, List[LRkItem], List[LRkItem]]`
            Success adding or detected reduction is `AddExtendReturn.REDUCE` or `ADD` or `CONFLICT`, if cannot add and reduce, return `AddExtendReturn.NONE`. After this, you need to cmp new and old closure to check the self loop in Graph if is `ADD` or `CONFLICT`. The reduce items is at the 2nd position in return. The add core items is at the 3rd position in return.
        """
        # Find GOTO
        is_add = False
        core_items: List[LRkItem] = []
        # traverse items
        for nonterminal in self.nonterminals:
            for item in self.symbol_LR_item_dict[nonterminal]:
                # try add symbol to item, and not change self.symbol_LR_item_dict
                if item.add(symbol):
                    core_items.append(item)
                    is_add = True
        # Find REDUCE
        is_reduce = False
        reduce_items: List[LRkItem] = []
        # traverse items
        for nonterminal in self.nonterminals:
            for item in self.symbol_LR_item_dict[nonterminal]:
                # try reduce item
                if item.is_on_reduce(symbol):
                    reduce_items.append(item)
                    is_reduce = True
        # Return Nothing
        if not is_add and not is_reduce:
            return self.AddExtendReturn.NONE, reduce_items, core_items
        if not is_add and is_reduce:
            return self.AddExtendReturn.REDUCE, reduce_items, core_items
        # check all recieved production to extend
        productions = self.recieved_productions
        check_list = []
        check_symbol = []
        for item in core_items:
            # check the follow symbol to extend
            check_symbol.append(item.production.sufs[item.dot_pos])
        list_len = -1
        while len(check_list) != list_len:
            list_len = len(check_list)
            for i in range(len(productions)):
                production = productions[i]
                if production.pre in check_symbol and i not in check_list:
                    check_symbol.append(production.sufs[0])
                    check_symbol = list(set(check_symbol))
                    check_list.append(i)
        self.recieved_productions = []
        core_productions = [item.production for item in core_items]
        for i in check_list:
            self.recieved_productions.append(productions[i])
        # collect extend productions into dict for find
        self.symbol_LR_item_dict = {}
        for production in self.recieved_productions:
            LR_item = LRkItem(production)
            if production.pre not in self.symbol_LR_item_dict:
                self.symbol_LR_item_dict[production.pre] = [LR_item]
            else:
                self.symbol_LR_item_dict[production.pre].append(LR_item)
        # add core items
        for i in range(len(core_items)):
            index = len(core_items) - 1 - i
            core_item = core_items[index]
            self.symbol_LR_item_dict[core_item.production.pre] = [
                core_item] + self.symbol_LR_item_dict[core_item.production.pre]
        self.recieved_productions = core_productions + self.recieved_productions

        # LR(0) is ok, next is for LR(1)

        self.first_dict: Dict[str, List[str]] = {}

        def find_first(self, first: str):
            # terminal is first
            if first in self.terminals:
                return [first]
            # searched first
            if first in self.first_dict:
                return self.first_dict[first]
            # nonterminal and unsearched, do it.
            first_list = []
            for LR_item in self.symbol_LR_item_dict[first]:
                first = LR_item.production.sufs[0]
                # next recurrence
                first_list += find_first(self, first)
            # add search result
            self.first_dict[first] = first_list
            # return to upper recurrence
            return first_list

        self.follow_dict: Dict[str, List[str]] = {}

        if self.k == 1:
            # calc FIRST set
            for nonterminal in self.nonterminals:
                find_first(self, nonterminal)
            # calc FOLLOW set
            for nonterminal in self.nonterminals:
                self.follow_dict[nonterminal] = []
            for nonterminal in self.nonterminals:
                for LR_item in self.symbol_LR_item_dict[nonterminal]:
                    if len(LR_item.production.sufs) < 2:
                        continue
                    # add '@EOF' for last one
                    if LR_item.production.sufs[-1] in self.nonterminals:
                        self.follow_dict[LR_item.production.sufs[-1]
                                         ].append('@EOF')
                    for symbol, follow_symbol in zip(LR_item.production.sufs[:-1], LR_item.production.sufs[1:]):
                        if symbol in self.nonterminals:
                            if follow_symbol in self.terminals:
                                self.follow_dict[symbol].append(follow_symbol)
                            else:
                                self.follow_dict[symbol] += self.first_dict[follow_symbol]
            # add lookahead terminals
            temp_symbol_LR_item_dict = {}
            for nonterminal in self.nonterminals:
                LR_items = []
                for LR_item in self.symbol_LR_item_dict[nonterminal]:
                    # do not change the core item
                    if LR_item.follow:
                        LR_items.append(LR_item)
                        continue
                    for follow in set(self.follow_dict[nonterminal]):
                        LR_item.set_follow([follow])
                        LR_items.append(LR_item)
                temp_symbol_LR_item_dict[nonterminal] = LR_items
            self.symbol_LR_item_dict = temp_symbol_LR_item_dict
        if is_reduce:
            return self.AddExtendReturn.CONFLICT, reduce_items, core_items
        else:
            return self.AddExtendReturn.ADD, reduce_items, core_items


def LR_item_cmp(LR_item_a: LRkItem, LR_item_b: LRkItem) -> bool:
    """
    Compare two `LRkItem` are equal

    Parameters
    ----------
    LR_item_a : :obj:`LRkItem`
        the first item
    LR_item_b : :obj:`LRkItem`
        the first item

    Returns
    -------
    bool
        equal is True
    """
    if LR_item_a.dot_pos != LR_item_b.dot_pos:
        return False
    if LR_item_a.follow != LR_item_b.follow:
        return False
    if LR_item_a.production.sufs != LR_item_b.production.sufs:
        return False
    if LR_item_a.production.pre != LR_item_b.production.pre:
        return False
    return True


def closure_cmp(closure_a: Closure, closure_b: Closure) -> bool:
    """
    Compare two `Closure` are equal

    Parameters
    ----------
    closure_a : :obj:`Closure`
        the first closure
    closure_b : :obj:`Closure`
        the first closure

    Returns
    -------
    bool
        equal is True
    """
    if closure_a.nonterminals == [] and closure_b.nonterminals == []:
        return True
    if closure_a.nonterminals != closure_b.nonterminals:
        return False
    if closure_a.terminals != closure_b.terminals:
        return False
    for nonterminal in closure_a.nonterminals:
        for item_a, item_b in zip(closure_a.symbol_LR_item_dict[nonterminal], closure_b.symbol_LR_item_dict[nonterminal]):
            if not LR_item_cmp(item_a, item_b):
                return False
    return True


class LRAction:
    """
    The LR Action is mainly defined the actions in LR, such as goto, reduce
    """

    ActionType = Enum('ActionType', 'GOTO REDUCE ACC ERR')

    def __init__(self, action_type: ActionType = ActionType.ERR, action_value: Any = None) -> None:
        """
        The LR Action is mainly defined the actions in LR, such as goto, reduce

        Parameters
        ----------
        action_type : :obj:`LRAction.ActionType`
            the type of action, includes `GOTO`, `REDUCE`, `ACC`, and `ERR`.
        action_value : :obj:`Any`, optional
            the value of action, None for `ACC`, int for `GOTO`, production for `REDUCE` 
        """
        self.action_type = action_type
        self.action_value = action_value


class LRTable:
    """
    The LR Table for action and goto. This is mainly defined this data structure. Construct LR table use :obj:`LR_table_construct()`.
    """

    def __init__(self, closure_num: int, terminals: List[str], nonterminals: List[str], prepared_dict: Dict[str, List[LRAction]] = {}) -> None:
        """
        The LR Table for action and goto. This is mainly defined this data structure.

        Parameters
        ----------
        closure_num : int
            the number of closures
        terminals : :obj:`list` of str
            the terminals of init closures
        nonterminals : :obj:`list` of str
            the nonterminals of init closures
        prepared_dict : :obj:`Dict[str, List[LRAction]]`, optional
            The inner prepared_dict if have. Reserve for deep copy. For normal usage, KEEP this empty '{}'. 
        """
        self._table_dict: Dict[str, List[LRAction]] = prepared_dict
        self.closure_num = closure_num
        self.terminals = terminals
        self.nonterminals = nonterminals
        # build empty dict
        if not prepared_dict:
            for i in terminals:
                self._table_dict[i] = [LRAction() for _ in range(closure_num)]
            for i in nonterminals:
                self._table_dict[i] = [LRAction() for _ in range(closure_num)]
            if '@EOF' not in self._table_dict:
                self.terminals.append('@EOF')
                self._table_dict['@EOF'] = [LRAction()
                                            for _ in range(closure_num)]

    def set_action(self, symbol: str, closure_index: int, action: LRAction) -> None:
        """
        Set the action in table. For the cell has not been set, default `ActionType.ERR`.

        Parameters
        ----------
        symbol : str
            the symbol of column
        closure_index : int
            the index of row
        action : :obj:`LRAction`
            the action
        """
        self._table_dict[symbol][closure_index] = action

    def get_action(self, symbol: str, closure_index: int) -> LRAction:
        """
        Get the action in table.

        Parameters
        ----------
        symbol : str
            the symbol of column
        closure_index : int
            the index of row
        """
        return self._table_dict[symbol][closure_index]

    def add_new_row(self):
        """
        Add a new row to this table
        """
        for k in list(self._table_dict.keys()):
            self._table_dict[k].append(LRAction())


ConflictType = Enum("ConflictType", "ShiftReduce MultiReduce")


def LR_table_construct(init_closure: Closure,
                       conflict_callback: Callable[[ConflictType, List[LRkItem], List[LRkItem]],
                                                   Tuple[Closure.AddExtendReturn, List[LRkItem], List[LRkItem]]]
                       ) -> LRTable:
    """
    The LR table constructor, just construct the table and callback the conflict, only include basic constructing operation.

    Parameters
    ----------
    init_closure : :obj:`Closure`
        the closure of augmented grammar
    conflict_callback
        The callback when the action conflict, such as goto-reduce conflict, it shoud be :obj:`Callable[[ConflictType, List[LRkItem], List[LRkItem]], Tuple[Closure.AddExtendReturn, List[LRkItem], List[LRkItem]]]` to adapt all conflit types like the return of :obj:`Closure.add_and_extend()`. For :obj:`ConflictType.MultiReduce` conflit, to choose one item to reduce or raise an exception. For :obj:`ConflictType.ShiftReduce`, to choose one action and return related data or raise an exception. This callback define like: `def callback(ct: ConflictType, reduce_items: List[LRkItem], add_core_items: List[LRkItem]) -> Tuple[Closure.AddExtendReturn, List[LRkItem], List[LRkItem]]`.
    """
    if '@EOF' not in init_closure.terminals:
        init_closure.terminals.append('@EOF')
    # Build init table
    nonterminals = init_closure.nonterminals
    # Remove Augmented Head
    nonterminals.remove(init_closure.recieved_productions[0].pre)
    table = LRTable(1, init_closure.terminals, nonterminals)
    # Scan the symbols
    closures = [init_closure]
    closure_index = 0
    # Action ACC first
    acc_closure = init_closure.deep_copy()
    ret, _, _ = acc_closure.add_and_extend(
        init_closure.recieved_productions[0].sufs[0])
    if ret == Closure.AddExtendReturn.ADD:
        if not closure_cmp(acc_closure, init_closure):
            closures.append(acc_closure)
            table.set_action(init_closure.recieved_productions[0].sufs[0], closure_index, LRAction(
                LRAction.ActionType.GOTO, len(closures) - 1))
            table.set_action('@EOF', len(closures) - 1,
                             LRAction(LRAction.ActionType.ACC))
    symbols = init_closure.terminals + nonterminals
    # Remove Augmented Body, since the body is the root of rest produtions, after adding ACC, NO MORE goto, NO MORE reduce
    symbols.remove(init_closure.recieved_productions[0].sufs[0])

    def try_symbols(old_closure, symbols, _closure_index):
        for symbol in symbols:
            new_closure = old_closure.deep_copy()
            ret, retr, reta = new_closure.add_and_extend(symbol)
            # Goto-Reduce Conflict
            if ret == Closure.AddExtendReturn.CONFLICT:
                ret, retr, reta = conflict_callback(
                    ConflictType.ShiftReduce, retr, reta)
            # GOTO
            if ret == Closure.AddExtendReturn.ADD:
                # Self circle
                if closure_cmp(new_closure, old_closure):
                    table.set_action(symbol, _closure_index, LRAction(
                        LRAction.ActionType.GOTO, _closure_index))
                else:  # Not self circle
                    closures.append(new_closure)
                    table.set_action(symbol, _closure_index, LRAction(
                        LRAction.ActionType.GOTO, len(closures) - 1))
            # REDUCE
            elif ret == Closure.AddExtendReturn.REDUCE:
                if len(retr) > 1:
                    ret, retr, reta = conflict_callback(
                        ConflictType.MultiReduce, retr, reta)
                    reduce_item: LRkItem = retr[0]
                elif len(retr) == 1:
                    reduce_item: LRkItem = retr[0]
                else:
                    e = Exception()
                    e.add_note("Should NOT be here!!!")
                    raise e
                table.set_action(symbol, _closure_index, LRAction(
                    LRAction.ActionType.REDUCE, reduce_item.production))

    try_symbols(init_closure, symbols, closure_index)
    closure_index = 2
    while closure_index < len(closures):
        try_symbols(closures[closure_index], symbols, closure_index)
        closure_index += 1
    return table


class LRTableERRException(Exception):
    """
    Exception when read ERR action in LRTable.
    """

    def __init__(self, parse_unit: ParseUnit, *args: object) -> None:
        """
        Exception when read ERR action in LRTable.

        Parameters
        ----------
        parse_unit : ParseUnit
            the one incur action ERR
        *args
            for super class Exception
        """
        super().__init__(*args)
        self.parse_unit = parse_unit

    def __str__(self) -> str:
        return f"LRTable ERR Error: The unit {self.parse_unit.name} in line {self.parse_unit.position[0]} col {self.parse_unit.position[0]} incurs the LR action of ERR. It is terminal? {self.parse_unit.is_terminator()}; Its value? {self.parse_unit.value}; Its property? {self.parse_unit.unit_property}."


class LRParserFramework(ParserFramework):
    """
    The basic LR Parser Framework for LR k=0,1.

    Parameters
    ----------
    self.k : int
        the k of LR, 0 or 1.
    self.acc : bool
        is or not reached ACC after parsing
    """

    def __init__(self, k=0) -> None:
        """
        The basic LR Parser Framework for LR k=0,1.

        Parameters
        ----------
        k : int
            the k of LR, 0 or 1.
        """
        super().__init__()
        self.k = k
        self.acc = False
        self._closure_index_stack = LifoQueue()

    def parse(self, parse_unit: ParseUnit) -> None:
        """
        Parse the lexical result. Before recieve lex results, you should :obj:`build_table()` as this func depends on LR Table.

        Parameters
        ----------
        parse_unit : :obj:`ParseUnit`
            the new :obj:`ParseUnit` from :obj:`ParserFramework.parse_lex_unit()` or :obj:`ParserFramework.parse_lex_unit_async()`
        """
        action = self._table.get_action(parse_unit.name, self._closure_index)

        def do_action(action):
            # ACC
            if action.action_type == LRAction.ActionType.ACC:
                self.acc = True
            # ERR
            elif action.action_type == LRAction.ActionType.ERR:
                raise LRTableERRException(parse_unit)
            # GOTO / Shift
            elif action.action_type == LRAction.ActionType.GOTO:
                self._closure_index = action.action_value
                self._closure_index_stack.put(self._closure_index)
            # REDUCE
            elif action.action_type == LRAction.ActionType.REDUCE:
                production: Production = action.action_value
                position: Tuple[int, int] = (0, 0)
                stack_parse_units: List[ParseUnit] = []
                # pop stack
                for _ in production.sufs:
                    stack_parse_unit: ParseUnit = self._stack.get()
                    position = stack_parse_unit.position
                    stack_parse_units.insert(0, stack_parse_unit)
                # invoke semant callback when production was reduced
                production.semant_callback(stack_parse_units)
                # put new reduced nonterminal to stack
                reduce_parse_unit: ParseUnit = ParseUnit(
                    production.pre, stack_parse_units, position, None, None)
                self._stack.put(reduce_parse_unit)
                # check which closure should goto
                closure_index = self._closure_index_stack.get()
                # ERR mean null when check after-reduce goto
                while self._table.get_action(production.pre, closure_index) == LRAction.ActionType.ERR:
                    closure_index = self._closure_index_stack.get()
                # get new action, if is goto just do it, if is reduce, then do reduce again. this may not be acc since acc is after one goto action.
                new_action = self._table.get_action(
                    production.pre, closure_index)
                do_action(new_action)

        do_action(action)
        # put new unit, shift it
        self._stack.put(parse_unit)

    def on_finish(self, value: Any = None, unit_property: Any = None) -> None:
        """
        Put @EOF to the stack, tell framework is finished. This func will invoke :obj:`parse()` to deal with EOF. After this, you can check :obj:`self.acc` is True or False.

        Parameters
        ----------
        value : optional
            reserved place for advanced usage, EOF's value of :obj:`ParseUnit`
        unit_property : optional
            reserved place for advanced usage, EOF's unit_property of :obj:`ParseUnit`
        """
        self.parse(ParseUnit('@EOF', [], (-1, -1), value, unit_property))

    def get_grammar_tree(self) -> ParseUnit:
        """
        Return the top :obj:`ParseUnit` (not the @EOF one, the real useful @S one) in stack, which includes the tree. You may invoke this after parsing.
        """
        for item in self._stack.queue:
            parse_item: ParseUnit = item
            if parse_item.name == "@S":
                return parse_item
        e = Exception()
        e.add_note("Not fund the '@S' unit.")
        raise e

    def build_table(self,
                    conflict_callback: Callable[[ConflictType, List[LRkItem], List[LRkItem]], Tuple[Closure.AddExtendReturn, List[LRkItem], List[LRkItem]]],
                    augmented_grammar_semant_callback: Callable[[
                        List[ParseUnit]], Any] = ParserFramework.none_semant_callback,
                    augmented_grammar_attr: Any = None
                    ) -> None:
        """
        Build the LR table for this framework. First, this will invoke :obj:`add_augmented_grammar()` to augment grammar. Then, build closure and table. Finally, save the table in this object.

        Parameters
        ----------
        conflict_callback : :obj:`Callable[[ConflictType, List[LRkItem], List[LRkItem]], Tuple[Closure.AddExtendReturn, List[LRkItem], List[LRkItem]]]`
            the callback for deal with the conflit. Yes, this is a basic class, conflit should deal in outter or higher class.
        augmented_grammar_semant_callback : :obj:`Callable[[List[ParseUnit]], Any]`, optional
            the semant callback for new production in augmented grammar in :obj:`add_augmented_grammar()`
        augmented_grammar_attr : optional
            the attr for new production in augmented grammar in :obj:`add_augmented_grammar()`
        """
        productions = add_augmented_grammar(
            self.productions, augmented_grammar_semant_callback, augmented_grammar_attr)
        init_closure = Closure(productions, self.k)
        self._table = LR_table_construct(init_closure, conflict_callback)
        self._closure_index: int = 0
        self._closure_index_stack.put(0)
