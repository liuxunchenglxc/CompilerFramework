from lexer_framework import HLlangLexerFramework, LexerFramework, LexerResult
from lr_parser import LR_0_Parser, LR_1_Parser, SLR_Parser
from parser_framework import ParseUnit
from typing import List
from io import StringIO
import unittest

class TestLR_ParserInMath(unittest.TestCase):
    """
    Test LR(0), SLR and LR(1) parsers in math expressions
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

    @staticmethod
    def _on_lexed_callback(lexer_result: LexerResult):
        return lexer_result.name != "Null"

    def _on_accepted_callback(self, lexer_result: LexerResult):
        self.parser.parse_lex_unit(lexer_result)

    def _on_finished_callback(self, num: int):
        self.parser.on_finish()
        print(f"Parsed {num} items.")

    def build_math_parser(self, k = 0, SLR = False):
        """
        Build a simple math parser
        """
        self.lexer = HLlangLexerFramework()

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

        self.lexer.on_lexed_callback = self._on_lexed_callback
        self.lexer.on_accepted_callback = self._on_accepted_callback
        self.lexer.on_finished_callback = self._on_finished_callback

        if k == 0:
            if SLR:
                self.parser = SLR_Parser()
            else:
                self.parser = LR_0_Parser()
        else:
            self.parser = LR_1_Parser()

        self.parser.add_semant_callback_dict("SemantAdd", self._sament_add)
        self.parser.add_semant_callback_dict("SemantSub", self._sament_sub)
        self.parser.add_semant_callback_dict("SemantMul", self._sament_mul)
        self.parser.add_semant_callback_dict("SemantDiv", self._sament_div)
        self.parser.add_semant_callback_dict("SemantSentValue0", self._sament_sent_value0)
        self.parser.add_semant_callback_dict("SemantSentValue1", self._sament_sent_value1)
        self.parser.add_semant_callback_dict("SemantAssign", self._sament_assign)

        if k == 0 and not SLR:
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
        self.assertTrue(self.parser.acc)
    
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
        self.assertTrue(self.parser.acc)

    def test_SLR(self):
        print()
        self.build_math_parser(SLR=True)
        s = "a = 1 + 2 * (3 - 4) / 5\n" \
            "b = 5+4*(3-2)/1\n" \
            "c=1+(2-3) * 4/5\n" \
            "d =5+(4 -  3)*2/1"
        print("Expression:")
        print(s, "\n")
        ss = StringIO(s)
        self.lexer.lex_stream(ss)
        self.assertTrue(self.parser.acc)


if __name__ == '__main__':
    unittest.main()
