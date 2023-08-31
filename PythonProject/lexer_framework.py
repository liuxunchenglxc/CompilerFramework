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

from typing import Callable, Any, List
import re

class IlleagalNameException(Exception):
    """
    Name of Item is illeagal
    """

    def __init__(self, name: str, *args: object) -> None:
        """
        Construct menthod

        Parameters
        ----------
        name : str
         error name
        *args : object
         for super class Exception
        """
        super().__init__(*args)
        self.name = name
    
    def __str__(self):
        return f"Illeagal Name: {self.name}. Name cannot start with '@'."

class LexItem:
    """
    The item of Lexer

    Members
    ----------
    self.name : str
     Name of Lex item
    self.format_cap_tex :  Callable[[str], Any]
     Callable of formatting the result of RegExpr
    self.regex : re.Pattern
     Regex operation
    """

    def __init__(self, name: str, format_cap_text: Callable[[str], Any]):
        """
        Construct method
         
        Parameters
        ----------
        name : str
         Name of Lex Item
        format_cap_text :  Callable[[str], Any]
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

    def set_regex(self, reg_expr: str, reg_flags: re.RegexFlag = re.NOFLAG):
        """
        Set the Regex
         
        Parameters
        ----------
        reg_expr : str
         Regular expression string
        reg_flags :  re.RegexFlag
         https://docs.python.org/3/library/re.html#flags
        """
        self.regex = re.compile(reg_expr, reg_flags)


class LexerFramework:
    """
    Framework of Lexer
    
    Members
    ----------
    self.lex_items : List[LexItem]
     Lex Items in list
    """

    def __init__(self, lex_items: List[LexItem] = []):
        """
        Construct menthod with LexItems
         
        Parameters
        ----------
        lex_items : List[LexItem]
         Prepared LexItems
        """
        self.lex_items = lex_items

    def add_lex_item(self, name: str, reg_expr: str, format_cap_text: Callable[[str], Any], reg_flags: re.RegexFlag = re.NOFLAG):
        """
        Add a Lex item, and Lex with this order.
         
        Parameters
        ----------
        name : str
         Name of item
        reg_expr : str
         Regular Expression of Lex, and automately add "^" at head
        format_cap_text : Callable[[str], Any]
         Callable of formatting the result of RegExpr
        reg_flags : re.RegexFlag
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
        self.lex_items.append(lex_item)

