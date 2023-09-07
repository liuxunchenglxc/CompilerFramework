Examples
=============
A simple math parser example for LR(0) and LR(1) Parsers in lr_parser.py
************************************************************************
.. code-block:: python

    """
    This example is also in unit_test.py.
    """
    from lexer_framework import HLlangLexerFramework, LexerFramework, LexerResult
    from lr_parser import LR_0_Parser, LR_1_Parser
    from parser_framework import ParseUnit
    from typing import List
    from io import StringIO


    class LR_ParserInMath:
    
        """
        The Semant Callback for calc the math expression, and passing the value
        """
        @staticmethod
        def _sament_add(parse_items: List[ParseUnit]):
            value1, value2 = parse_items[0].value, parse_items[2].value
            res = float(value1) + float(value2)
            print("Add:", *[i.value for i in parse_items], "->", res)
            return res
        
        @staticmethod
        def _sament_sub(parse_items: List[ParseUnit]):
            value1, value2 = parse_items[0].value, parse_items[2].value
            res = float(value1) - float(value2)
            print("Sub:", *[i.value for i in parse_items], "->", res)
            return res
        
        @staticmethod
        def _sament_mul(parse_items: List[ParseUnit]):
            value1, value2 = parse_items[0].value, parse_items[2].value
            res = float(value1) * float(value2)
            print("Mul:", *[i.value for i in parse_items], "->", res)
            return res
        
        @staticmethod
        def _sament_div(parse_items: List[ParseUnit]):
            value1, value2 = parse_items[0].value, parse_items[2].value
            res = float(value1) / float(value2)
            print("Div:", *[i.value for i in parse_items], "->", res)
            return res
        
        @staticmethod
        def _sament_assign(parse_items: List[ParseUnit]):
            value2 = parse_items[2].value
            print("Assign:", *[i.value for i in parse_items])
            return float(value2)
        
        @staticmethod
        def _sament_sent_value0(parse_items: List[ParseUnit]):
            value = parse_items[0].value
            return value
        
        @staticmethod
        def _sament_sent_value1(parse_items: List[ParseUnit]):
            value = parse_items[1].value
            return value
    
        """
        The callbacks to recieve the results from Lexical Analysis and invoke Parser.
        """
        @staticmethod
        def _on_lexed_callback(lexer_result: LexerResult):
            return lexer_result.name != "Null"
    
        def _on_accepted_callback(self, lexer_result: LexerResult):
            self.parser.parse_lex_unit(lexer_result)
    
        def _on_finished_callback(self, num: int):
            self.parser.on_finish()
            print(f"Parsed {num} items.")
    
        """
        Build the math lexer and parser
        """
        def build_math_parser(self, k = 0):
            self.lexer = HLlangLexerFramework()
            # Add the regex rules
            self.lexer.add_operators("(", LexerFramework.none_format_cap_text, 0, 0, "\\(")
            self.lexer.add_operators(")", LexerFramework.none_format_cap_text, 0, 0, "\\)")
            self.lexer.add_operators("Add", LexerFramework.none_format_cap_text, 0, 0, "\\+")
            self.lexer.add_operators("Sub", LexerFramework.none_format_cap_text, 0, 0, "-")
            self.lexer.add_operators("Mul", LexerFramework.none_format_cap_text, 0, 0, "\\*")
            self.lexer.add_operators("Div", LexerFramework.none_format_cap_text, 0, 0, "/")
            self.lexer.add_operators("Assign", LexerFramework.none_format_cap_text, 0, 0, "=")
            self.lexer.add_constants("Number", HLlangLexerFramework.convert_float, 0, 0, False, "(-|\\+)?\\d+(\\.\\d+)?")
            self.lexer.add_identifier("Variable")
            self.lexer.add_lex_item("Null", "\\s+", HLlangLexerFramework.drop_null)
            # Add the lexer callback
            self.lexer.on_lexed_callback = self._on_lexed_callback
            self.lexer.on_accepted_callback = self._on_accepted_callback
            self.lexer.on_finished_callback = self._on_finished_callback
            # Choose the Parser
            if k == 0:
                self.parser = LR_0_Parser()
            else:
                self.parser = LR_1_Parser()
            # Add the semant callbacks for math calc and value passing
            self.parser.add_semant_callback_dict("SemantAdd", self._sament_add)
            self.parser.add_semant_callback_dict("SemantSub", self._sament_sub)
            self.parser.add_semant_callback_dict("SemantMul", self._sament_mul)
            self.parser.add_semant_callback_dict("SemantDiv", self._sament_div)
            self.parser.add_semant_callback_dict("SemantSentValue0", self._sament_sent_value0)
            self.parser.add_semant_callback_dict("SemantSentValue1", self._sament_sent_value1)
            self.parser.add_semant_callback_dict("SemantAssign", self._sament_assign)
            # Set different productions for LR(0) and LR(1)
            if k == 0:
                # LR(0) support +,-,*,/
                self.parser.add_production_by_multi_str("SSS -> SS SSS", # Multi sentences
                                                        "SSS -> SS",
                                                        "SS -> Variable Assign S @SemantAssign", # sentence
                                                        "S -> S Add EA @SemantAdd$priority=10", # right part
                                                        "S -> EA @SemantSentValue0",
                                                        "EA -> EA Sub ES @SemantSub$priority=10",
                                                        "EA -> ES @SemantSentValue0",
                                                        "ES -> ES Mul EM @SemantMul$priority=20",
                                                        "ES -> EM @SemantSentValue0",
                                                        "EM -> EM Div V @SemantDiv$priority=20",
                                                        "EM -> V @SemantSentValue0",
                                                        "V -> Number @SemantSentValue0",
                                                        "V -> Variable @SemantSentValue0")
            else:
                # LR(1) support +,-,*,/,(,)
                self.parser.add_production_by_multi_str("SSS -> SS SSS", # Multi sentences
                                                        "SSS -> SS",
                                                        "SS -> Variable Assign S @SemantAssign", # sentence
                                                        "S -> S Add S @SemantAdd$priority=10", # right part
                                                        "S -> S Sub S @SemantSub$priority=10",
                                                        "S -> S Mul S @SemantMul$priority=20",
                                                        "S -> S Div S @SemantDiv$priority=20",
                                                        "S -> ( S ) @SemantSentValue1",
                                                        "S -> V @SemantSentValue0",
                                                        "V -> Number @SemantSentValue0",
                                                        "V -> Variable @SemantSentValue0")
            # Build LR Table
            self.parser.build_table()
    
        def test_LR_0(self):
            print()
            self.build_math_parser()
            s = "a = 1 + 2 * 3 - 4 / 5\n" \
                "b = 5+4*3-2/1\n" \
                "c=1+2-3 * 4/5\n" \
                "d =5+4 -  3*2/1"
            print("Expression:")
            print(s, "\n")
            ss = StringIO(s)
            self.lexer.lex_stream(ss)
            print(f"The parser test result is {self.parser.acc}")
        
        def test_LR_1(self):
            print()
            self.build_math_parser(k=1)
            s = "a = 1 + 2 * (3 - 4) / 5\n" \
                "b = 5+4*(3-2)/1\n" \
                "c=1+(2-3) * 4/5\n" \
                "d =5+(4 -  3)*2/1"
            print("Expression:")
            print(s, "\n")
            ss = StringIO(s)
            self.lexer.lex_stream(ss)
            print(f"The parser test result is {self.parser.acc}")

    if __name__ == '__main__':
        LR_ParserInMath().test_LR_0()
        LR_ParserInMath().test_LR_1()

This should output:
.. code-block:: python

    Expression:
    a = 1 + 2 * 3 - 4 / 5
    b = 5+4*3-2/1
    c=1+2-3 * 4/5
    d =5+4 -  3*2/1

    Mul: 2.0 * 3.0 -> 6.0
    Div: 4.0 / 5.0 -> 0.8
    Sub: 6.0 - 0.8 -> 5.2
    Add: 1.0 + 5.2 -> 6.2
    Assign: a = 6.2
    Mul: 4.0 * 3.0 -> 12.0
    Div: 2.0 / 1.0 -> 2.0
    Sub: 12.0 - 2.0 -> 10.0
    Add: 5.0 + 10.0 -> 15.0
    Assign: b = 15.0
    Div: 4.0 / 5.0 -> 0.8
    Mul: 3.0 * 0.8 -> 2.4000000000000004
    Sub: 2.0 - 2.4000000000000004 -> -0.40000000000000036
    Add: 1.0 + -0.40000000000000036 -> 0.5999999999999996
    Assign: c = 0.5999999999999996
    Div: 2.0 / 1.0 -> 2.0
    Mul: 3.0 * 2.0 -> 6.0
    Sub: 4.0 - 6.0 -> -2.0
    Add: 5.0 + -2.0 -> 3.0
    Assign: d = 3.0
    Parsed 44 items.
    The parser test result is True

    Expression:
    a = 1 + 2 * (3 - 4) / 5
    b = 5+4*(3-2)/1
    c=1+(2-3) * 4/5
    d =5+(4 -  3)*2/1

    Sub: 3.0 - 4.0 -> -1.0
    Div: -1.0 / 5.0 -> -0.2
    Mul: 2.0 * -0.2 -> -0.4
    Add: 1.0 + -0.4 -> 0.6
    Assign: a = 0.6
    Sub: 3.0 - 2.0 -> 1.0
    Div: 1.0 / 1.0 -> 1.0
    Mul: 4.0 * 1.0 -> 4.0
    Add: 5.0 + 4.0 -> 9.0
    Assign: b = 9.0
    Sub: 2.0 - 3.0 -> -1.0
    Div: 4.0 / 5.0 -> 0.8
    Mul: -1.0 * 0.8 -> -0.8
    Add: 1.0 + -0.8 -> 0.19999999999999996
    Assign: c = 0.19999999999999996
    Sub: 4.0 - 3.0 -> 1.0
    Div: 2.0 / 1.0 -> 2.0
    Mul: 1.0 * 2.0 -> 2.0
    Add: 5.0 + 2.0 -> 7.0
    Assign: d = 7.0
    Parsed 52 items.
    The parser test result is True
