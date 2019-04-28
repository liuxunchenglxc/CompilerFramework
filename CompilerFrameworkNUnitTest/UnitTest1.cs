//    CompilerFramework NUnitTest
//    Copyright(C) 2019  ¡ı—∏≥–

//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.

//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
//    GNU General Public License for more details.

//    You should have received a copy of the GNU General Public License
//    along with this program.If not, see<https://www.gnu.org/licenses/>.
using NUnit.Framework;
using CompilerFramework.Lexer;
using System.IO;
using System.Collections.Generic;

namespace CompileTests
{
    public class LexerTests
    {
        LexerFramework LexerFramework;
        List<KeyValuePair<string, object>> Lexeresults;
        public FormatCapTextDelegate formatNullDelegate;
        public object FormatNull(string capText)
        {
            return null;
        }
        public FormatCapTextDelegate formatDigitDelegate;
        public object FormateDigit(string capText)
        {
            return long.Parse(capText);
        }
        public bool OnLexd(LexerFramework sender, LexerResult e)
        {
            Lexeresults.Add(new KeyValuePair<string, object>(e.Name, e.Value));
            return true;
        }

        [SetUp]
        public void Setup()
        {
            Lexeresults = new List<KeyValuePair<string, object>>();
            LexerFramework = new LexerFramework();
            formatNullDelegate = FormatNull;
            LexerFramework.AddLexItem("Null", @"[\s]", formatNullDelegate);
            LexerFramework.AddLexItem("Type", "int");
            LexerFramework.AddLexItem("Operator", "=");
            LexerFramework.AddLexItem("Delimiter", ";");
            formatDigitDelegate = FormateDigit;
            LexerFramework.AddLexItem("Digit", "[0-9]+", formatDigitDelegate);
            LexerFramework.AddLexItem("Identifier", "[A-Za-z][A-Za-z0-9_]*");
            LexerFramework.OnLexedEventHandler += OnLexd;
        }
        [Test]
        public void TestAddLexItem()
        {
            Assert.AreEqual(LexerFramework.LexItems[0].Count, 6);
        }
        [Test]
        public void TestLexStream()
        {
            long i = LexerFramework.LexStream(new StringReader("int"));
            Assert.AreEqual(1, i);
            i = LexerFramework.LexStream(new StringReader("  "));
            Assert.AreEqual(0, i);
            i = LexerFramework.LexStream(new StringReader("a"));
            Assert.AreEqual(1, i);
            i = LexerFramework.LexStream(new StringReader("a_1"));
            Assert.AreEqual(1, i);
            i = LexerFramework.LexStream(new StringReader("123"));
            Assert.AreEqual(1, i);
        }
        /// <summary>
        /// test: int a = 1;
        /// </summary>
        [Test]
        public void Test1()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;"));
            Assert.AreEqual(5, i);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>
            {
                new KeyValuePair<string, object>("Type", "int"),
                new KeyValuePair<string, object>("Identifier", "a"),
                new KeyValuePair<string, object>("Operator", "="),
                new KeyValuePair<string, object>("Digit", 1),
                new KeyValuePair<string, object>("Delimiter", ";")
            };
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n"));
            Assert.AreEqual(5, i);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n  int a = 1;"));
            Assert.AreEqual(i, 10);
        }
    }
    class HLLexTest
    {
        HLlangLexerFramework LexerFramework;
        List<KeyValuePair<string, object>> Lexeresults;
        public bool OnLexed(LexerFramework sender, LexerResult e)
        {
            switch (sender.CurrentLexGroup)
            {
                case 0:
                    if (e.Name == "Annotation")
                    {
                        if ((string)e.Value == "//") sender.CurrentLexGroup = 1;// single line annotation
                        if ((string)e.Value == "/*") sender.CurrentLexGroup = 2;// multi-line annotation
                        return false;
                    }
                    else
                    {
                        // save the result
                        Lexeresults.Add(new KeyValuePair<string, object>(e.Name, e.Value));
                        return true;
                    }
                case 1:
                    sender.CurrentLexGroup = 0;// back to normal group.
                    return false;
                case 2:
                    if (e.Name == "Annotation") sender.CurrentLexGroup = 0;// back to normal group.
                    return false;
                default:
                    return false;
            }
        }

        public void OnFinished(LexerFramework sender, long e)
        {
            Assert.AreEqual(5, e);
        }

        [SetUp]
        public void Setup()
        {
            Lexeresults = new List<KeyValuePair<string, object>>();
            LexerFramework = new HLlangLexerFramework(3);
            //Group 0 for normal Lex
            LexerFramework.AddLexItem("Null", @"\s+", x => null);
            LexerFramework.AddResWords("Type", null, 0, "int", "long", "float", "double", "string", "char", "bool");
            LexerFramework.AddResWords("ResWord", null, 0, "struct", "class", "void", "public", "private");
            LexerFramework.AddDelimiters("Annotation", null, 0, "//", @"/\*");
            LexerFramework.AddOperators("Operator", null, 0, "==", "!=", ">=", "<=", "&&", @"\|\|", @"\*\*", "=", "!", "&", @"\|", "<", ">", @"\*", @"\+", "-", "/", @"\\", "%");
            LexerFramework.AddDelimiters("Delimiter", null, 0, ";", ":", @"\.", ",", "{", "}");
            LexerFramework.AddConstants("String", null, 0, true, "(?=\").*(?=\")");
            LexerFramework.AddConstants("AtString", null, 0, true, "(?=@\").*(?=\")");
            LexerFramework.AddConstants("Char", null, 0, true, "'.'");
            LexerFramework.AddConstants("Real", x => double.Parse(x), 0, false, @"(-|\+?)\d+\.\d+");
            LexerFramework.AddConstants("Digit", x => long.Parse(x), 0, false, @"(-|\+?)[0-9]+");
            LexerFramework.AddConstants("Bool", x => bool.Parse(x), 0, true, "true|false");
            LexerFramework.AddIdentifier();
            //Group 1 for single line annotation
            LexerFramework.CurrentAddGroupNumber = 1;
            LexerFramework.AddLexItem("AnnotationContext", @".+");
            //Group 2 for multiple line annotation
            LexerFramework.CurrentAddGroupNumber = 2;
            LexerFramework.AddDelimiters("Annotation", null, 0, @".*\*/");
            LexerFramework.AddLexItem("AnnotationContext", @".+$", x => null);
            //Bound Event
            LexerFramework.OnLexedEventHandler += OnLexed;
        }
        [Test]
        public void TestAddLexItem()
        {
            Assert.IsNotEmpty(LexerFramework.LexItems);
        }
        [Test]
        public void TestLexStream()
        {
            long i = LexerFramework.LexStream(new StringReader("int"));
            Assert.AreEqual(1, i);
            i = LexerFramework.LexStream(new StringReader("  "));
            Assert.AreEqual(0, i);
            i = LexerFramework.LexStream(new StringReader("a"));
            Assert.AreEqual(1, i);
            i = LexerFramework.LexStream(new StringReader("a_1"));
            Assert.AreEqual(1, i);
            i = LexerFramework.LexStream(new StringReader("123"));
            Assert.AreEqual(1, i);
        }
        /// <summary>
        /// test: int a = 1;
        /// </summary>
        [Test]
        public void Test1()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;"));
            Assert.AreEqual(5, i);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>
            {
                new KeyValuePair<string, object>("Type", "int"),
                new KeyValuePair<string, object>("Identifier", "a"),
                new KeyValuePair<string, object>("Operator", "="),
                new KeyValuePair<string, object>("Digit", 1),
                new KeyValuePair<string, object>("Delimiter", ";")
            };
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n"));
            Assert.AreEqual(5, i);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n  int a = 1;"));
            Assert.AreEqual(10, i);
            i = LexerFramework.LexStream(new StringReader("double a = 1.123;\r\n"));
            Assert.AreEqual(5, i);
            LexerFramework.OnFinishedEventHandler += OnFinished;
            i = LexerFramework.LexStream(new StringReader("bool a = true;\r\n"));
            Assert.AreEqual(5, i);
        }
        [Test]
        public void TestSingleLineAnnotation()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;// this is single line annotation"));
            Assert.AreEqual(5, i);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>
            {
                new KeyValuePair<string, object>("Type", "int"),
                new KeyValuePair<string, object>("Identifier", "a"),
                new KeyValuePair<string, object>("Operator", "="),
                new KeyValuePair<string, object>("Digit", 1),
                new KeyValuePair<string, object>("Delimiter", ";")
            };
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;// this is single line annotation\r\n" +
                "int a = 1;"));
            Assert.AreEqual(10, i);
        }
        [Test]
        public void TestMultiLineAnnotation()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;/* this is \r\n multiple line \r\n annotation */"));
            Assert.AreEqual(5, i);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>
            {
                new KeyValuePair<string, object>("Type", "int"),
                new KeyValuePair<string, object>("Identifier", "a"),
                new KeyValuePair<string, object>("Operator", "="),
                new KeyValuePair<string, object>("Digit", 1),
                new KeyValuePair<string, object>("Delimiter", ";")
            };
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;/* this is \r\n multiple line \r\n annotation */" +
                "int a = 1;"));
            Assert.AreEqual(10, i);
        }
        [Test]
        public void TestZeroLenght()
        {
            try
            {
                LexerFramework.CurrentAddGroupNumber = 0;
                LexerFramework.AddLexItem("Zero", "|");
                LexerFramework.LexStream(new StringReader("@@@@@"));
                Assert.Fail();
            }
            catch(ZeroLenghtMatchException e)
            {
                Assert.AreEqual("Zero", e.Name);
                Assert.AreEqual("^|", e.RegExpr);
            }
        }
        [Test]
        public void TestNotFound()
        {
            try
            {
                LexerFramework.CurrentAddGroupNumber = 0;
                LexerFramework.LexStream(new StringReader("@@@@@"));
                Assert.Fail();
            }
            catch (NoMatchException e)
            {
                Assert.AreEqual(1, e.Col);
                Assert.AreEqual(1, e.Line);
            }
        }
        [Test]
        public void TestGroupNum()
        {
            try
            {
                LexerFramework.CurrentAddGroupNumber = 4;
                LexerFramework.AddLexItem("Zero", "|");
                Assert.Fail();
            }
            catch (GroupNumException e)
            {
                Assert.AreEqual(4, e.Num);
            }
        }
    }
}
