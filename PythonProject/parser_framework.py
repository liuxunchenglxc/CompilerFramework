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

from typing import Callable, Any, List, Tuple, Dict
import time
from queue import LifoQueue

from lexer_framework import LexerResult


class ParseUnit:
    """
    Unit of Parse, such as phrase.

    Parameters
    ----------
    self.name : str
        name of this, such as "class"
    self.parse_units : :obj:`list` of :obj:`ParseUnit`
        the unit contained, as son nodes
    self.position : :obj:`Tuple` of (int, int)
        position of unit (line, col)
    self.value : :obj:`Any`
        reserved place for advanced usage
    self.unit_property : :obj:`Any`
        reserved place for advanced usage
    """

    def __init__(self, name: str, parse_units: List, position: Tuple[int, int], value: Any, unit_property: Any) -> None:
        """
        Unit of Parse, such as phrase.

        Parameters
        ----------
        name : str
            name of this, such as "class"
        parse_units : :obj:`list` of :obj:`ParseUnit`
            the unit contained, as son nodes
        position : :obj:`Tuple` of (int, int)
            position of unit (line, col)
        value : :obj:`Any`
            reserved place for advanced usage
        unit_property : :obj:`Any`
            reserved place for advanced usage
        """
        self.name = name
        self.parse_units = parse_units
        self.position = position
        self.value = value
        self.unit_property = unit_property

    def is_terminator(self) -> bool:
        """
        is terminator, if no children.
        """
        return len(self.parse_units) == 0


class Production:
    """
    the production of grammar

    Parameters
    ----------
    self.pre : str
        antecedent
    self.sufs : :obj:`list` of str
        seccedents
    self.semant_callback : :obj:`Callable` of :obj:`list` of :obj:`ParseUnit` with return of :obj:`Any`
        callback for semanting
    self.attr : :obj:`Any`
        attr for advansing usage
    """

    def __init__(self, pre: str, sufs: List[str], semant_callback: Callable[[List[ParseUnit]], Any], attr: Any) -> None:
        """
        the production of grammar

        Parameters
        ----------
        pre : str
            antecedent
        sufs : :obj:`list` of str
            seccedents
        semant_callback : :obj:`Callable` of :obj:`list` of :obj:`ParseUnit` with return of :obj:`Any`
            callback for semanting
        attr : :obj:`Any`
            attr for advansing usage
        """
        self.pre = pre
        self.sufs = sufs
        self.semant_callback = semant_callback
        self.attr = attr

    def deep_copy(self):
        """
        Deep copy self
        """
        return Production(self.pre, [i for i in self.sufs], self.semant_callback, self.attr)


class ParseIndexException(Exception):
    """
    Exception when index is not match
    """

    def __init__(self, index_p: int, index_l: int, *args: object) -> None:
        """
        Exception when index is not match

        Parameters
        ----------
        index_p : int
            index should be (of parser)
        index_l : int
            current index (of lexer_result)
        *args
            for super class Exception
        """
        super().__init__(*args)
        self.index_p = index_p
        self.index_l = index_l

    def __str__(self) -> str:
        return f"Index Error: Index should be {self.index_p} instead of {self.index_l}"


class WaitTimeoutException(Exception):
    """
    Exception when `parse_lex_unit_async` waits timeout
    """

    def __init__(self, index_p: int, index_l: int, *args: object) -> None:
        """
        Exception when `parse_lex_unit_async` waits timeout

        Parameters
        ----------
        index_p : int
            index should be (of parser)
        index_l : int
            current index (of lexer_result)
        *args
            for super class Exception
        """
        super().__init__(*args)
        self.index_p = index_p
        self.index_l = index_l

    def __str__(self) -> str:
        return f"Wait Timeout: Index processing: {self.index_p}, this index is {self.index_l}"


class ProductSentenceException(Exception):
    """
    Exception when `product_sentence` is illeagal.
    """

    def __init__(self, product_sentence: str, *args: object) -> None:
        """
        Exception when `product_sentence` is illeagal.

        Parameters
        ----------
        product_sentence : str
            Error Sentence
        *args
            for super class Exception
        """
        super().__init__(*args)
        self.product_sentence = product_sentence

    def __str__(self) -> str:
        return f"ProductSentence Error: sentence \"{self.product_sentence}\" is illeagal."


class ParserFramework:
    """
    The very base framework of parsing, provide very base methods for all kind of parsing.

    Parameters
    ----------
    self._index : int
        For the parsing order checking.
    self._stack : :obj:`LifoQueue`
        stack for PDA
    self.productions : :obj:`list` of :obj:`Production`
        collection of productions
    self.semant_callback_dict : :obj:`dict` of str to :obj:`Callable` of :obj:`list` of :obj:`ParseUnit` with return of :obj:`Any`
        Semant Callback Dictionary for string convert to callback.
    """

    def __init__(self) -> None:
        self._index = 0
        self._stack = LifoQueue()
        self.productions: List[Production] = []
        self.semant_callback_dict: Dict[str,
                                        Callable[[List[ParseUnit]], Any]] = {}

    def parse(self, parse_unit: ParseUnit) -> None:
        """
        parsing entrance abstract method, you need to override this method.

        Parameters
        ----------
        parse_unit : :obj:`ParseUnit`
            parse unit
        """
        pass

    ###################################
    # receive result of lexing region #
    ###################################

    def parse_lex_unit(self, lexer_result: LexerResult) -> None:
        """
        Receive LexerResult and Parse synchronously, order of `lexer_result.index` will be check.

        Parameters
        ----------
        lexer_result : :obj:`LexerResult`
            The Result of Lexer

        Raises
        ------
        ParseIndexException
            when index is not match
        """
        # check the order
        if lexer_result.index != self._index:
            raise ParseIndexException(self._index, lexer_result.index)
        # transfer to parse unit
        parse_unit = ParseUnit(lexer_result.name, [],
                               lexer_result.position, lexer_result.value, None)
        # to parse it
        self.parse(parse_unit)
        # move to next
        self._index += 1

    async def parse_lex_unit_async(self, lexer_result: LexerResult, timeout: int = 600) -> None:
        """
        Receive LexerResult and Parse asynchronously, order of `lexer_result.index` will be checked. The author suggests to use `asyncio.create_task()` to invoke this method/function. This impl is different from C# version, the inner includes a waiting loop for matching `lexer_result.index`.

        Parameters
        ----------
        lexer_result : :obj:`LexerResult`
            The Result of Lexer
        timeout : int
            The wait timeout seconds

        Raises
        ------
        WaitTimeoutException
            when this waits timeout for matching `lexer_result.index`.
        """
        # The author changed the impl of ansyc task instead of C# version
        # wait for index, this can be cause dead loop if you DO NOT correctly use this framework.
        timeout = 100 * timeout  # 10 minus default
        now = 0
        while lexer_result.index != self._index:
            time.sleep(0.01)
            now += 1
            if now > timeout:
                raise WaitTimeoutException(self._index, lexer_result.index)
        # now is this index time
        # transfer to parse unit
        parse_unit = ParseUnit(lexer_result.name, [],
                               lexer_result.position, lexer_result.value, None)
        # to parse it
        self.parse(parse_unit)
        # move to next
        self._index += 1

    ##############################
    # receive productions region #
    ##############################

    def add_production(self, production: Production) -> None:
        """
        the most direct way to add `production`

        Parameters
        ----------
        production : :obj:`Production`
            production
        """
        self.productions.append(production)

    def add_semant_callback_dict(self, name: str, semant_callback: Callable[[List[ParseUnit]], Any]) -> None:
        """
        part of indirect way of add `production`, add the `semant_callback` to dict.

        Parameters
        ----------
        name : str
            name of semant_callback, the key in dict
        semant_callback : :obj:`Callable` of :obj:`list` of :obj:`ParseUnit` with return :obj:`Any`
            the callback when reduce one production for semant analysis
        """
        self.semant_callback_dict[name] = semant_callback

    @staticmethod
    def none_semant_callback(parse_units: List[ParseUnit]) -> Any:
        return None

    def add_production_by_str(self, product_sentence: str):
        """
        indirect way of add production by string, format string `product_sentence` as:
        `Pre ->|:|| Suf0 Suf1 ... [@SemantCallbackName[$attr]]`

        `$attr` is as: `$key1=value1[&key2=value2[&...]]`

        like this:
        `E -> F G`

        or like this:
        `E -> E add E @SemantAdd`

        or like this:
        `E | E opt E @SementOpt`

        or like this:
        `E : Delimiter E Delimiter @Semant`

        or with attr in string (attr will be string type), just add `$attr` directly behand `@SemantDelegateName`:
        `E -> E F @Semant$priority=0&attr2=xxx`

        If you need Semant Callback, please add `semant_callback` use `add_semant_callback_dict` first.

        Parameters
        ----------
        product_sentence : str
            formated string

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
        production = Production(vs[0], sufs, semant_callback, attr)
        self.add_production(production)

    def add_production_by_multi_str(self, *product_sentences: str) -> None:
        """
        indirect way of add production by strings, each format string in `product_sentences` as:
        `Pre ->|:|| Suf0 Suf1 ... [@SemantCallbackName[$attr]]`

        like this:
        `E -> F G`

        or like this:
        `E -> E add E @SemantAdd`

        or like this:
        `E | E opt E @SementOpt`

        or like this:
        `E : Delimiter E Delimiter @Semant`

        or with attr in string (attr will be string type), just add `$attr` directly behand `@SemantDelegateName`:
        `E -> E F @Semant$deal`

        If you need Semant Callback, please add `semant_callback` use `add_semant_callback_dict` first.

        Parameters
        ----------
        product_sentences : :obj:`tuple` of str
            formated strings

        Raises
        ------
        ProductSentenceException
            if one product sentence in `product_sentences` is illeagal
        """
        for ps in product_sentences:
            self.add_production_by_str(ps)
