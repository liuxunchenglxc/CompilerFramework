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
import re
import io

class IlleagalNameException(Exception):
    """
    Name of Item is illeagal
    """

    def __init__(self, name: str, *args: object) -> None:
        """
        Construct menthod

        Parameters
        ----------
        name: str
         error name
        *args: object
         for super class Exception
        """
        super().__init__(*args)
        self.name = name
    
    def __str__(self):
        return f"Illeagal Name: {self.name}. Name cannot start with '@'."

class ZeroLenghtMatchException(Exception):
    """
    Exception produeced while match zero width
    """

    def __init__(self, name: str, pattern: str, *args: object) -> None:
        """
        Construct menthod

        Parameters
        ----------
        name: str
         error lex name
        pattern: str
         error reg pattern
        *args: object
         for super class Exception
        """
        super().__init__(*args)
        self.name = name
        self.pattern = pattern
    
    def __str__(self):
        return f"Lex Error: Zero Length String Matched, indicating end-less loop, by Name: {self.name}, RegExpr: {self.pattern}"

class GroupNumException(Exception):
    """
    Exception produeced while group number is too small or too large
    """

    def __init__(self, group: int, *args: object) -> None:
        """
        Construct menthod

        Parameters
        ----------
        group: int
         error group index
        *args: object
         for super class Exception
        """
        super().__init__(*args)
        self.group = group
    
    def __str__(self):
        return f"AddLexItem Error: illeagal Lex group number: {self.group}"

class NoMatchException(Exception):
    """
    Exception produeced while no lex items in group match the rest text.
    """

    def __init__(self, line: int, col: int, *args: object) -> None:
        """
        Construct menthod

        Parameters
        ----------
        line: int
         error line number
        col: int
         error column number
        *args: object
         for super class Exception
        """
        super().__init__(*args)
        self.line = line
        self.col = col
    
    def __str__(self):
        return f"Lex Error: Cannot match words at line {self.line} and column {self.col}"

class LexItem:
    """
    The item of Lexer

    Members
    ----------
    self.name: str
     Name of Lex item
    self.format_cap_tex:  Callable[[str], Any]
     Callable of formatting the result of RegExpr
    self.regex: re.Pattern
     Regex operation
    """

    def __init__(self, name: str, format_cap_text: Callable[[str], Any]):
        """
        Construct method
         
        Parameters
        ----------
        name: str
         Name of Lex Item
        format_cap_text : Callable[[str], Any]
         Callable of formatting the result of RegExpr
         
        Raises
        ------
        IlleagalNameException
         when name start with '@'
        """
        if re.match("^@.*", name) is not None:
            raise IlleagalNameException(name)
        self.name = name
        self.format_cap_text = format_cap_text

    def set_regex(self, reg_expr: str, reg_flags: re.RegexFlag = re.NOFLAG) -> None:
        """
        Set the Regex
         
        Parameters
        ----------
        reg_expr: str
         Regular expression string
        reg_flags:  re.RegexFlag
         https://docs.python.org/3/library/re.html#flags
        """
        self.regex = re.compile(reg_expr, reg_flags)

class LexerResult:
    """
    Lex Result

    Members
    ----------
    self.index: int
     Order of Lex result
    self.name: str
     Name of Lex Item
    self.value: Any
     Value of Lex result
    self.position: Tuple[int, int]
     position of item (line, col)
    """

    def __init__(self, index: int, name: str, value: Any, line: int, col: int):
        """
        Construct method
         
        Parameters
        ----------
        index: int
         Order of Lex result
        name: str
         Name of Lex Item
        value: Any
         Value of Lex result
        line: int
         line number
        col: int
         column number
        """
        self.index = index
        self.name = name
        self.value = value
        self.position = (line, col)

class LexerFramework:
    """
    Framework of Lexer
    
    Members
    ----------
    self.lex_item_groups: List[List[LexItem]]
     Groups of Lex Items in list
    self.on_lexed_callback: Callable[[LexerResult], bool]
     the callback when single Lex result produced to judge whether accept this lex result.
    self.on_accepted_callback: Callable[[LexerResult]
     the callback when single Lex result accepted by on_lexed_callback
    """

    def __init__(self, lex_item_groups: List[List[LexItem]] = [[]]):
        """
        Construct menthod with LexItems
         
        Parameters
        ----------
        lex_items: List[LexItem]
         Prepared LexItemGroups
        """
        self.lex_item_groups = lex_item_groups

    def add_lex_group(self, lex_items: List[LexItem] = []):
        """
        Add a new group of lex items.

        Parameters
        ----------
        lex_items: List[LexItem]
         new group of lex items
        """
        self.lex_item_groups.append(lex_items)

    @staticmethod
    def non_format_cap_text(s: str) -> Any:
        return s

    def add_lex_item(self, name: str, reg_expr: str, format_cap_text: Callable[[str], Any] = non_format_cap_text, reg_flags: re.RegexFlag = re.NOFLAG, group: int = 0) -> None:
        """
        Add a Lex item, and Lex with this order.
         
        Parameters
        ----------
        name: str
         Name of item
        reg_expr: str
         Regular Expression of Lex, and automately add "^" at head
        format_cap_text: Callable[[str], Any]
         Callable of formatting the result of RegExpr
        reg_flags: re.RegexFlag
         https://docs.python.org/3/library/re.html#flags
        """
        if name is None:
            return
        if reg_expr is None:
            return
        lex_item = LexItem(name, format_cap_text)
        if reg_expr[0] != '^':
            reg_expr = '^' + reg_expr
        lex_item.set_regex(reg_expr, reg_flags)
        if group >= len(self.lex_item_groups) or group < 0:
            raise GroupNumException(group)
        self.lex_item_groups[group].append(lex_item)

    def set_on_lexed_callback(self, callback: Callable[[LexerResult], bool]) -> None:
        """
        Set the callback when single Lex result produced. Accept(return true) or not(return false) the single lex result.
        
        Callback Parameters
        ----------
        1: LexerResult
         one result of lex
        """
        self.on_lexed_callback = callback

    def set_on_accepted_callback(self, callback: Callable[[LexerResult], None]) -> None:
        """
        Set the callback when single Lex result accepted by on_lexed_callback, and you need to choice which parser framework you need in paring.
        
        Callback Parameters
        ----------
        1: LexerResult
         one result of lex
        """
        self.on_accepted_callback = callback

    def set_on_finished_callback(self, callback: Callable[[int], None]) -> None:
        """
        Set the callback when all lex is done.
        
        Callback Parameters
        ----------
        1: int
         the total number of lex results
        """
        self.on_finished_callback = callback

    def _lex_single_line(self, s: str, lex_item: LexItem, index: int, line: int, col: int) -> Tuple[str, int]:
        """
        Lex a single line string, if formated value equal null, then drop it and return true.
         
        Parameters
        ----------
        s: str
         that string will be Lexed
        lex_item: LexItem
         Lex item for Lex string
        index: int
         index of Lex result
        line: int
         line number
        col: int
         column number

        Returns
        -------
        Tuple[str, int]
         new trimed string and the new index

        Raises
        ------
        ZeroLenghtMatchException
         when match the zero length word
        """
        match = lex_item.regex.match(s)
        if match is None:
            return s, index
        result = match.group()
        if result is None:
            raise ZeroLenghtMatchException(lex_item.name, lex_item.regex.pattern)
        value = lex_item.format_cap_text(result)
        if value:
            lexer_result = LexerResult(index, lex_item.name, value, line, col)
            if self.on_lexed_callback(lexer_result):
                index += 1
                self.on_accepted_callback(lexer_result)
        s = s[len(result):]
        return s, index

    def lex_stream(self, text_reader: io.IOBase, group: int = 0) -> int:
        """
        Lex multiple lines string stream(io.StringIO) or file stream(with open() func), but as single line read-parttern. If formated value equal null, then drop it. By the way, please get the result from on_lexed_callback(for filting result) and set_on_accepted_callback(for getting result) one by one. For example, you can write a collector for receiving results.
         
        Parameters
        ----------
        s: str
         that multiple lines string will be Lexed
        group: int
         the Lex Group, for advanced usage, eg. you can define multiple groups and use LexerFramework for different scenarios..

        Returns
        -------
        int
         the count of results

        Raises
        ------
        NoMatchException
         if input line cannot be matched by Lex items
        """
        if self.lex_item_groups[group] is None:
            return 0
        index = 0
        line = 0
        pos = -1
        while text_reader.tell() == pos:
            pos = text_reader.tell()
            line_text = str(text_reader.readline()).strip()
            line += 1
            col_num = len(line_text)
            while line_text:
                is_match = False
                col = col_num - len(line_text) + 1
                for lex_item in self.lex_item_groups[group]:
                    line_text, new_index = self._lex_single_line(line_text, lex_item, index, line, col)
                    if new_index != index:
                        is_match = True
                        index = new_index
                        col = col_num - len(line_text) + 1
                if not is_match:
                    raise NoMatchException(line, col)
        self.on_finished_callback(index)
        return index

