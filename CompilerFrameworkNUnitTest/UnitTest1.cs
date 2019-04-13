using NUnit.Framework;
using CompilerFramework;
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
        public bool OnLexd(LexerFramework sender, Lexeresult e)
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
            LexerFramework.OnLexdEventHandler += OnLexd;
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
            Assert.AreEqual(i, 1);
            i = LexerFramework.LexStream(new StringReader("  "));
            Assert.AreEqual(i, 0);
            i = LexerFramework.LexStream(new StringReader("a"));
            Assert.AreEqual(i, 1);
            i = LexerFramework.LexStream(new StringReader("a_1"));
            Assert.AreEqual(i, 1);
            i = LexerFramework.LexStream(new StringReader("123"));
            Assert.AreEqual(i, 1);
        }
        /// <summary>
        /// test: int a = 1;
        /// </summary>
        [Test]
        public void Test1()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;"));
            Assert.AreEqual(i, 5);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>();
            test.Add(new KeyValuePair<string, object>("Type", "int"));
            test.Add(new KeyValuePair<string, object>("Identifier", "a"));
            test.Add(new KeyValuePair<string, object>("Operator", "="));
            test.Add(new KeyValuePair<string, object>("Digit", 1));
            test.Add(new KeyValuePair<string, object>("Delimiter", ";"));
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n"));
            Assert.AreEqual(i, 5);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n  int a = 1;"));
            Assert.AreEqual(i, 10);
        }
    }
    class HLLexTest
    {
        HLlangLexerFramework LexerFramework;
        List<KeyValuePair<string, object>> Lexeresults;
        public bool OnLexd(LexerFramework sender, Lexeresult e)
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

        [SetUp]
        public void Setup()
        {
            Lexeresults = new List<KeyValuePair<string, object>>();
            LexerFramework = new HLlangLexerFramework(3);
            //Group 0 for normal Lex
            LexerFramework.AddLexItem("Null", @"\s+", x => null);
            LexerFramework.AddResWordsLexItem("Type", null, 0, "int", "long", "float", "double", "string", "char", "bool");
            LexerFramework.AddResWordsLexItem("ResWord", null, 0, "struct", "class", "void", "public", "private");
            LexerFramework.AddDelimitersLexItem("Annotation", null, 0, "//", @"/\*");
            LexerFramework.AddOperatorsLexItem("Operator", null, 0, "==", "!=", ">=", "<=", "&&", @"\|\|", @"\*\*", "=", "!", "&", @"\|", "<", ">", @"\*", @"\+", "-", "/", @"\\", "%");
            LexerFramework.AddDelimitersLexItem("Delimiter", null, 0, ";", ":", @"\.", ",", "{", "}");
            LexerFramework.AddConstantsLexItem("String", null, 0, true, "(?=\").*(?=\")");
            LexerFramework.AddConstantsLexItem("AtString", null, 0, true, "(?=@\").*(?=\")");
            LexerFramework.AddConstantsLexItem("Char", null, 0, true, "'.'");
            LexerFramework.AddConstantsLexItem("Real", x => double.Parse(x), 0, false, @"(-|\+?)\d+\.\d+");
            LexerFramework.AddConstantsLexItem("Digit", x => long.Parse(x), 0, false, @"(-|\+?)[0-9]+");
            LexerFramework.AddConstantsLexItem("Bool", x => bool.Parse(x), 0, true, "true|false");
            LexerFramework.AddIdentifierLexItem();
            //Group 1 for single line annotation
            LexerFramework.CurrentAddGroupNumber = 1;
            LexerFramework.AddLexItem("AnnotationContext", @".+");
            //Group 2 for multiple line annotation
            LexerFramework.CurrentAddGroupNumber = 2;
            LexerFramework.AddDelimitersLexItem("Annotation", null, 0, @".*\*/");
            LexerFramework.AddLexItem("AnnotationContext", @".+$", x => null);
            //Bound Event
            LexerFramework.OnLexdEventHandler += OnLexd;
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
            Assert.AreEqual(i, 1);
            i = LexerFramework.LexStream(new StringReader("  "));
            Assert.AreEqual(i, 0);
            i = LexerFramework.LexStream(new StringReader("a"));
            Assert.AreEqual(i, 1);
            i = LexerFramework.LexStream(new StringReader("a_1"));
            Assert.AreEqual(i, 1);
            i = LexerFramework.LexStream(new StringReader("123"));
            Assert.AreEqual(i, 1);
        }
        /// <summary>
        /// test: int a = 1;
        /// </summary>
        [Test]
        public void Test1()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;"));
            Assert.AreEqual(i, 5);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>();
            test.Add(new KeyValuePair<string, object>("Type", "int"));
            test.Add(new KeyValuePair<string, object>("Identifier", "a"));
            test.Add(new KeyValuePair<string, object>("Operator", "="));
            test.Add(new KeyValuePair<string, object>("Digit", 1));
            test.Add(new KeyValuePair<string, object>("Delimiter", ";"));
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n"));
            Assert.AreEqual(i, 5);
            i = LexerFramework.LexStream(new StringReader("int a = 1;\r\n  int a = 1;"));
            Assert.AreEqual(i, 10);
        }
        [Test]
        public void TestSingleLineAnnotation()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;// this is single line annotation"));
            Assert.AreEqual(i, 5);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>();
            test.Add(new KeyValuePair<string, object>("Type", "int"));
            test.Add(new KeyValuePair<string, object>("Identifier", "a"));
            test.Add(new KeyValuePair<string, object>("Operator", "="));
            test.Add(new KeyValuePair<string, object>("Digit", 1));
            test.Add(new KeyValuePair<string, object>("Delimiter", ";"));
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;// this is single line annotation\r\n" +
                "int a = 1;"));
            Assert.AreEqual(i, 10);
        }
        [Test]
        public void TestMultiLineAnnotation()
        {
            long i = LexerFramework.LexStream(new StringReader("int a = 1;/* this is \r\n multiple line \r\n annotation */"));
            Assert.AreEqual(i, 5);
            List<KeyValuePair<string, object>> test = new List<KeyValuePair<string, object>>();
            test.Add(new KeyValuePair<string, object>("Type", "int"));
            test.Add(new KeyValuePair<string, object>("Identifier", "a"));
            test.Add(new KeyValuePair<string, object>("Operator", "="));
            test.Add(new KeyValuePair<string, object>("Digit", 1));
            test.Add(new KeyValuePair<string, object>("Delimiter", ";"));
            Assert.AreEqual(test, Lexeresults);
            i = LexerFramework.LexStream(new StringReader("int a = 1;/* this is \r\n multiple line \r\n annotation */" +
                "int a = 1;"));
            Assert.AreEqual(i, 10);
        }
    }
}
