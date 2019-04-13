using System;
using CompilerFramework;
using System.IO;
using System.Collections.Generic;

namespace CompilerFrameworkDemo
{
    class DemoClangWithBaseFramework
    {
        HLlangLexerFramework LexerFramework;

        public List<KeyValuePair<string, object>> Lexeresults { get; set; }

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
        void SetUpLexer()
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
        public DemoClangWithBaseFramework()
        {
            SetUpLexer();
        }
        public long LexStream(TextReader textReader) => LexerFramework.LexStream(textReader);
    }
    class Program
    {
        static void Main(string[] args)
        {
            DemoClangWithBaseFramework demoClangWithBaseFramework = new DemoClangWithBaseFramework();
            if (args.Length == 0)
            {
                Console.WriteLine("Please input one line code:");
                string s = Console.ReadLine();
                long i = 0;
                try
                {
                    i = demoClangWithBaseFramework.LexStream(new StringReader(s));
                }
                catch (LexerFrameException e)
                {
                    Console.WriteLine(e.Message);
                }
                Console.WriteLine("The number of Lexs is " + i);
                foreach (KeyValuePair<string, object> keyValuePair in demoClangWithBaseFramework.Lexeresults)
                {
                    Console.WriteLine("Name:" + keyValuePair.Key + " Value:" + keyValuePair.Value);
                }
                Console.Read();
            }
            else
            {
                foreach (string arg in args)
                {
                    long i = 0;
                    try
                    {
                        i = demoClangWithBaseFramework.LexStream(new StringReader(arg));
                    }
                    catch (LexerFrameException e)
                    {
                        Console.WriteLine(e.Message);
                    }
                    Console.WriteLine("The number of Lexs is " + i);
                    foreach (KeyValuePair<string, object> keyValuePair in demoClangWithBaseFramework.Lexeresults)
                    {
                        Console.WriteLine("Name:" + keyValuePair.Key + " Value:" + keyValuePair.Value);
                    }
                    Console.WriteLine();
                }
                Console.Read();
            }
        }
    }
}

