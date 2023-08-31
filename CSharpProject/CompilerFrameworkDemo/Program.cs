//    CompilerFramework Demo
//    Copyright(C) 2019  刘迅承

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
using System;
using CompilerFramework.Lexer;
using System.IO;
using System.Collections.Generic;

namespace CompilerFrameworkDemo
{
    class PartialClangDemo
    {
        // using high level framework
        HLlangLexerFramework LexerFramework;
        // results collection
        public List<KeyValuePair<string, object>> Lexeresults { get; set; }
        // deal with different results, and contral the lex groups.
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
                    // single line annotation back to normal
                    sender.CurrentLexGroup = 0;// back to normal group.
                    return false;
                case 2:
                    // multiple line annotation back to normal
                    if (e.Name == "Annotation") sender.CurrentLexGroup = 0;// back to normal group.
                    return false;
                default:
                    return false;
            }
        }
        void SetUpLexer()
        {
            // initialize the results collector
            Lexeresults = new List<KeyValuePair<string, object>>();
            // initialize LexerFramework with three lex groups
            LexerFramework = new HLlangLexerFramework(3);

            // Group 0 for normal Lex

            // drop all blank words
            LexerFramework.AddLexItem("Null", @"\s+", x => null);

            // add Reserved Words first, to avoid be cover by others in matching
            // to distinguish the type reserved words
            LexerFramework.AddResWords("Type", null, 0, "int", "long", "float", "double", "string", "char", "bool");
            // you can also distinguish other reserved words or not
            LexerFramework.AddResWords("ResWord", null, 0, "struct", "class", "void", "public", "private");

            // add all kinds of symbols
            // composite symbol fisrt, such as "//",">=" .etc
            LexerFramework.AddDelimiters("Annotation", null, 0, "//", @"/\*");
            // be careful of Regular Expression Symbols and transfer its meaning 
            LexerFramework.AddOperators("Operator", null, 0, "==", "!=", ">=", "<=", "&&", @"\|\|", @"\*\*", "=", "!", "&", @"\|", "<", ">", @"\*", @"\+", "-", "/", @"\\", "%");
            // rest of symbols
            LexerFramework.AddDelimiters("Delimiter", null, 0, ";", ":", @"\.", ",", "{", "}");

            // add all kinds of Constants
            // normal string
            LexerFramework.AddConstants("String", null, 0, true, "(?=\").*(?=\")");
            // un-transferred-meaning string
            LexerFramework.AddConstants("AtString", null, 0, true, "(?=@\").*(?=\")");
            // char
            LexerFramework.AddConstants("Char", null, 0, true, "'.'");
            // double type number
            LexerFramework.AddConstants("Real", x => double.Parse(x), 0, false, @"(-|\+?)\d+\.\d+");
            // int/long type number
            LexerFramework.AddConstants("Digit", x => long.Parse(x), 0, false, @"(-|\+?)[0-9]+");
            // boolean type
            LexerFramework.AddConstants("Bool", x => bool.Parse(x), 0, true, "true|false");

            // add indentifier define (start with [a-zA-Z] and follow [a-zA-Z0-9_]* as normal)
            LexerFramework.AddIdentifier();

            // Group 1 for single line annotation

            // set which group you want to add
            LexerFramework.CurrentAddGroupNumber = 1;
            // add single line annotation context lex item
            LexerFramework.AddLexItem("AnnotationContext", @".+");

            // Group 2 for multiple line annotation

            // set which group you want to add
            LexerFramework.CurrentAddGroupNumber = 2;
            // add multiple line annotation end-word lex item
            LexerFramework.AddDelimiters("Annotation", null, 0, @".*\*/");
            // add multiple line annotation context lex item
            LexerFramework.AddLexItem("AnnotationContext", @".+$", x => null);

            // Bound OnLexed Event
            LexerFramework.OnLexedEventHandler += OnLexed;
        }
        public PartialClangDemo()
        {
            SetUpLexer();
        }
        public long LexStream(TextReader textReader) => LexerFramework.LexStream(textReader);
    }
    class Program
    {
        static void Main(string[] args)
        {
            PartialClangDemo demoClangWithBaseFramework = new PartialClangDemo();
            if (args.Length == 0)
            {
                Console.WriteLine("Please input one line code:");
                string s = Console.ReadLine();
                long i = 0;
                try
                {
                    i = demoClangWithBaseFramework.LexStream(new StringReader(s));
                }
                catch (NoMatchException e)
                {
                    Console.WriteLine(e.Message);
                }
                catch (ZeroLenghtMatchException e)
                {
                    Console.WriteLine(e.Message);
                }
                catch (GroupNumException e)
                {
                    Console.WriteLine(e.Message);
                }
                // show results
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
                    catch (NoMatchException e)
                    {
                        Console.WriteLine(e.Message);
                    }
                    catch (ZeroLenghtMatchException e)
                    {
                        Console.WriteLine(e.Message);
                    }
                    catch (GroupNumException e)
                    {
                        Console.WriteLine(e.Message);
                    }
                    // show results
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

