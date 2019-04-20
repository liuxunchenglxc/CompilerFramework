//    CompilerFramework
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
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;

namespace CompilerFramework.Lexer
{
    /// <summary>
    /// Framework of Lexer
    /// </summary>
    public class LexerFramework
    {
        /// <summary>
        /// The number of LexGroups
        /// </summary>
        public int LexGroupCount { get; }
        /// <summary>
        /// For advanced usage, like multi-entrance processing.
        /// </summary>
        public int CurrentLexGroup { get; set; }
        /// <summary>
        /// Single Lex result receive delegate
        /// </summary>
        /// <param name="e">The single result of Lex</param>
        /// <param name="sender">Incoming object</param>
        /// <returns>Is count this Lex result, and accept it to parse</returns>
        public delegate bool OnLexedDelegate(LexerFramework sender, LexerResult e);
        /// <summary>
        /// When single Lex result produced
        /// </summary>
        public event OnLexedDelegate OnLexedEventHandler;
        /// <summary>
        /// Single Lex result is accepted to parse by OnLexed
        /// </summary>
        /// <param name="sender">Incoming object</param>
        /// <param name="e">The single result of Lex</param>
        public delegate void OnAcceptedDelegate(LexerFramework sender, LexerResult e);
        /// <summary>
        /// When single Lex result accepted by OnLexed, and you need to choice which parser framework you need in paring.
        /// </summary>
        public event OnAcceptedDelegate OnAcceptedEventHandler;
        /// <summary>
        /// The list of Lex items, defualt use [0], others for advanced usage.
        /// </summary>
        public List<LexItem>[] LexItems { get; private set; }
        /// <summary>
        /// Default construct menthod
        /// </summary>
        public LexerFramework()
        {
            LexGroupCount = 1;
            LexItems = new List<LexItem>[1];
            LexItems[0] = new List<LexItem>();
        }
        /// <summary>
        /// Construct menthod with multi-group processing
        /// </summary>
        public LexerFramework(int groupCount)
        {
            LexGroupCount = groupCount;
            LexItems = new List<LexItem>[groupCount];
            for (int i = 0; i < groupCount; i++)
            {
                LexItems[i] = new List<LexItem>();
            }
        }
        /// <summary>
        /// Construct menthod with LexItems
        /// </summary>
        /// <param name="lexItems">Prepared LexItems</param>
        public LexerFramework(List<LexItem>[] lexItems)
        {
            LexGroupCount = LexItems.Length;
            LexItems = lexItems;
        }
        /// <summary>
        /// Add a Lex item, and Lex with this order.
        /// </summary>
        /// <param name="name">Name of item</param>
        /// <param name="regExpr">Regular Expression of Lex, and automately add "^" at head</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExpr</param>
        /// <param name="group">LexGroup for advanced usage</param>
        /// <exception cref="GroupNumException">if Lex group number is out of limite or under zero</exception>
        public void AddLexItem(string name, string regExpr, FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None, int group = 0)
        {
            if (name.Length == 0) return;
            if (regExpr.Length == 0) return;
            LexItem LexItem = new LexItem(name, formatCapTextDelegate);
            if (!regExpr.StartsWith('^')) regExpr = '^' + regExpr;// reg expr must start from head of string
            LexItem.SetRegex(regExpr, regexOptions);
            if (group >= LexGroupCount || group < 0) throw new GroupNumException(group,"AddLexItem Error: illeagal Lex group number: " + group);
            LexItems[group].Add(LexItem);
        }
        /// <summary>
        /// Lex multiple lines string or file from TextReader, but as single line read-parttern.
        /// If formated value equal null, then drop it.
        /// By the way, please get the result from OnLexdHandler one by one.
        /// For example, you can write a collector for receiving results.
        /// </summary>
        /// <param name="textReader">TextReader of string or file</param>
        /// <param name="group">LexGroup for advanced usage</param>
        /// <returns>the count of results</returns>
        /// <exception cref="NoMatchException">if input cannot be matched by Lex items</exception>
        public long LexStream(TextReader textReader, int group = 0)
        {
            CurrentLexGroup = group;
            if (LexItems[CurrentLexGroup].Count == 0) return 0;
            long sumCount = 0;
            long lineNum = 0;
            while (textReader.Peek() != -1)// ensure not end
            {
                string LexObject = textReader.ReadLine();// read one line and deal with it
                lineNum++;
                int colNum = LexObject.Length;
                while (LexObject.Length != 0)// ensure not null
                {
                    bool isMatch = false;
                    int resCol = colNum - LexObject.Length + 1;
                    foreach (LexItem LexItem in LexItems[CurrentLexGroup])// match by order once
                    {
                        if (LexString(ref LexObject, LexItem, ref sumCount, lineNum, resCol))
                        {
                            isMatch = true;
                            break;// continuous operate
                        }
                    }
                    if (!isMatch)
                    {
                        throw new NoMatchException(lineNum, resCol, "Lex Error: Cannot match words at line " + lineNum + " and column " + resCol + ".");
                    }
                }
            }
            return sumCount;
        }
        /// <summary>
        /// Lex a single line string, if formated value equal null, then drop it and return true.
        /// </summary>
        /// <param name="LexObject">that string will be Lexd</param>
        /// <param name="LexItem">Lex item for Lex string</param>
        /// <param name="count">count of Lex result</param>
        /// <param name="line">line number</param>
        /// <param name="col">column number</param>
        /// <returns>match result</returns>
        /// <exception cref="ZeroLenghtMatchException">if match zero lenght string</exception>
        private bool LexString(ref string LexObject, LexItem LexItem, ref long count, long line, int col)
        {
            Match match = LexItem.Regex.Match(LexObject);// match reg expr
            if (!match.Success) return false;
            string result = match.Value;
            if (result.Length == 0) throw new ZeroLenghtMatchException(LexItem.Name, LexItem.Regex.ToString(), "Lex Error: Zero Length String Matched, " +
                "indicating end-less loop, by Name:" + LexItem.Name + " RegExpr:" + LexItem.Regex.ToString());
            object value;
            if (LexItem.FormatCapText == null) value = result;
            else value = LexItem.FormatCapText(result);// format the result
            if (value != null)
            {
                LexerResult Lexeresult = new LexerResult(count, LexItem.Name, value, line, col); // save the result
                // call event to notice user to receive it
                if (OnLexedEventHandler(this, Lexeresult))
                {
                    count++; // must be one result for the start with "^" parttern
                    OnAcceptedEventHandler(this, Lexeresult);// to parse it.
                }
            }
            int restLenght = LexObject.Length - match.Length;
            LexObject = LexObject.Substring(match.Length, restLenght);// for continuous operate
            return true;
        }
    }
    /// <summary>
    /// The item of Lexer
    /// </summary>
    [Serializable]
    public struct LexItem
    {
        /// <summary>
        /// Name of Lex item
        /// </summary>
        public string Name { get; }
        /// <summary>
        /// The delegate of formatting the result of RegExpr
        /// </summary>
        public FormatCapTextDelegate FormatCapText { get; }
        internal Regex Regex { get; private set; }
        /// <summary>
        /// Set the Regex
        /// </summary>
        public void SetRegex(string regExpr, RegexOptions regOptions)
        {
            Regex = new Regex(regExpr, regOptions);
        }
        /// <summary>
        /// Construct method
        /// </summary>
        /// <param name="name">Name of Lex Item</param>
        /// <param name="formatCapText">The delegate of formatting the result of RegExpr</param>
        public LexItem(string name, FormatCapTextDelegate formatCapText)
        {
            Name = name;
            FormatCapText = formatCapText;
            Regex = null;
        }
    }
    /// <summary>
    /// The delegate of formatting CapText.
    /// </summary>
    /// <param name="capText">capText by RegExpr</param>
    /// <returns></returns>
    public delegate object FormatCapTextDelegate(string capText);
    /// <summary>
    /// Lex Result
    /// </summary>
    [Serializable]
    public struct LexerResult
    {
        /// <summary>
        /// Order of Lex result
        /// </summary>
        public long Index { get; }
        /// <summary>
        /// Name of Lex result
        /// </summary>
        public string Name { get; }
        /// <summary>
        /// Value of Lex result, if you not define the type of this, its string.
        /// </summary>
        public object Value { get; }
        /// <summary>
        /// position of item
        /// </summary>
        public Position Position{get;}

        /// <summary>
        /// Construct method
        /// </summary>
        /// <param name="index">Order of Lex result</param>
        /// <param name="name">Name of Lex result</param>
        /// <param name="value">Value of Lex result</param>
        /// <param name="col">column number</param>
        /// <param name="line">line number</param>
        public LexerResult(long index, string name, object value, long line, int col)
        {
            Index = index;
            Name = name;
            Value = value;
            Position = new Position(line, col);
        }
    }
    /// <summary>
    /// High level programing language Lexer framework
    /// </summary>
    public sealed class HLlangLexerFramework : LexerFramework
    {
        /// <summary>
        /// Construct a Lexer with one processing group.
        /// </summary>
        public HLlangLexerFramework() : base() { }
        /// <summary>
        /// For advanced usage, like mutli-entrance processing
        /// </summary>
        /// <param name="groupCount">the number of group</param>
        public HLlangLexerFramework(int groupCount) : base(groupCount) { }
        /// <summary>
        /// Construct menthod with LexItems
        /// </summary>
        /// <param name="LexItems">Prepared LexItems</param>
        public HLlangLexerFramework(List<LexItem>[] LexItems) : base(LexItems) { }
        /// <summary>
        /// Which LexGroup you want to add items.
        /// </summary>
        public int CurrentAddGroupNumber { get; set; } = 0;
        /// <summary>
        /// Add a Lex item in group of AddCurrentGroupNumber, and Lex with this order.
        /// </summary>
        /// <param name="name">Name of item</param>
        /// <param name="regExpr">Regular Expression of Lex, and automately add "^" at head</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExpr</param>
        public void AddLexItem(string name, string regExpr, FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None)
        {
            AddLexItem(name, regExpr, formatCapTextDelegate, regexOptions, CurrentAddGroupNumber);
        }
        /// <summary>
        /// Add reserved words Lex items, and recomand to do this before add indentifier Lex item.
        /// </summary>
        /// <param name="name">Name of Lex items</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExprs</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="regExprs">Regular Expressions of Lex items, and auto add <c>(?=\W|$)</c> to the end</param>
        public void AddResWords(string name = "ResWord", FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None, params string[] regExprs)
        {
            for (int i = 0; i < regExprs.Length; i++)
            {
                if (!regExprs[i].EndsWith(@"(?=\W|$)")) regExprs[i] += @"(?=\W|$)";
                AddLexItem(name, regExprs[i], formatCapTextDelegate, regexOptions, CurrentAddGroupNumber);
            }
        }
        /// <summary>
        /// Add identifier Lex item, and recomand to do this after add reserved words Lex item.
        /// </summary>
        /// <param name="name">Name of Lex item</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExprs</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="regExpr">Regular Expression of Lex item</param>
        public void AddIdentifier(string name = "Identifier", FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None, string regExpr = @"[A-Za-z]\w*")
        {
            AddLexItem(name, regExpr, formatCapTextDelegate, regexOptions, CurrentAddGroupNumber);
        }
        /// <summary>
        /// Add operators Lex items, and recomand to add composite operators first.
        /// </summary>
        /// <param name="name">Name of Lex items</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExprs</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="regExprs">Regular Expressions of Lex items</param>
        public void AddOperators(string name = "Operator", FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None, params string[] regExprs)
        {
            for (int i = 0; i < regExprs.Length; i++)
            {
                AddLexItem(name, regExprs[i], formatCapTextDelegate, regexOptions, CurrentAddGroupNumber);
            }
        }
        /// <summary>
        /// Add Delimiters Lex items, and recomand to add composite delimiters first.
        /// </summary>
        /// <param name="name">Name of Lex items</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExprs</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="regExprs">Regular Expressions of Lex items</param>
        public void AddDelimiters(string name = "Delimiter", FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None, params string[] regExprs)
        {
            for (int i = 0; i < regExprs.Length; i++)
            {
                AddLexItem(name, regExprs[i], formatCapTextDelegate, regexOptions, CurrentAddGroupNumber);
            }
        }
        /// <summary>
        /// Add Constants Lex items, and recomand to add composite constants first.
        /// </summary>
        /// <param name="name">Name of Lex items</param>
        /// <param name="formatCapTextDelegate">The delegate of formatting the result of regExprs</param>
        /// <param name="regexOptions">Regular Expression Options</param>
        /// <param name="isAddZeroWidthAssertion">Is auto add <c>(?=\w|$)</c> to the end of RegExprs</param>
        /// <param name="regExprs">Regular Expressions of Lex items</param>
        public void AddConstants(string name = "Constant", FormatCapTextDelegate formatCapTextDelegate = null, RegexOptions regexOptions = RegexOptions.None, bool isAddZeroWidthAssertion = true, params string[] regExprs)
        {
            for (int i = 0; i < regExprs.Length; i++)
            {
                if (!regExprs[i].EndsWith(@"(?=\W|$)") && isAddZeroWidthAssertion) regExprs[i] += @"(?=\W|$)";
                AddLexItem(name, regExprs[i], formatCapTextDelegate, regexOptions, CurrentAddGroupNumber);
            }
        }
        /// <summary>
        /// As FormatCapTextDelegate defined, deal with blank words.
        /// </summary>
        /// <param name="s">string to be drap</param>
        /// <returns>null</returns>
        public static object DropNull(string s) => null;
        /// <summary>
        /// As FormatCapTextDelegate defined, deal with int words.
        /// </summary>
        /// <param name="s">string to be int</param>
        /// <returns>int object</returns>
        public static object ConvertInt(string s) => int.Parse(s);
        /// <summary>
        /// As FormatCapTextDelegate defined, deal with long int words.
        /// </summary>
        /// <param name="s">string to be long int</param>
        /// <returns>long int object</returns>
        public static object ConvertLong(string s) => long.Parse(s);
        /// <summary>
        /// As FormatCapTextDelegate defined, deal with float words.
        /// </summary>
        /// <param name="s">string to be int</param>
        /// <returns>float object</returns>
        public static object ConvertFloat(string s) => float.Parse(s);
        /// <summary>
        /// As FormatCapTextDelegate defined, deal with double words.
        /// </summary>
        /// <param name="s">string to be double</param>
        /// <returns>double object</returns>
        public static object ConvertDouble(string s) => double.Parse(s);

    }
    /// <summary>
    /// Exception produeced while cannot match.
    /// </summary>
    public class NoMatchException : Exception
    {
        /// <summary>
        /// Error line
        /// </summary>
        public long Line { get; }
        /// <summary>
        /// Error column
        /// </summary>
        public int Col { get; }
        /// <summary>
        /// Construct menthod
        /// </summary>
        /// <param name="lineNum">error line</param>
        /// <param name="colNum">error column</param>
        /// <param name="message">error message</param>
        public NoMatchException(long lineNum, int colNum, string message) : base(message)
        {
            Line = lineNum;
            Col = colNum;
        }
    }
    /// <summary>
    /// Exception produeced while group num is illeagal.
    /// </summary>
    public class GroupNumException : Exception
    {
        /// <summary>
        /// Error num
        /// </summary>
        public long Num { get; }
        /// <summary>
        /// Construct menthod
        /// </summary>
        /// <param name="num">error group num</param>
        /// <param name="message">error message</param>
        public GroupNumException(int num, string message) : base(message)
        {
            Num = num;
        }
    }
    /// <summary>
    /// Exception produeced while match zero width
    /// </summary>
    public class ZeroLenghtMatchException : Exception
    {
        /// <summary>
        /// name of LexItem
        /// </summary>
        public string Name { get; }
        /// <summary>
        /// regular expression with danger
        /// </summary>
        public string RegExpr { get; }
        /// <summary>
        /// Construct menthod
        /// </summary>
        /// <param name="name">name of LexItem</param>
        /// <param name="regExpr">regular expression with danger</param>
        /// <param name="message">error message</param>
        public ZeroLenghtMatchException(string name, string regExpr, string message) : base(message)
        {
            Name = name;
            RegExpr = regExpr;
        }
    }
    /// <summary>
    /// Position of unit
    /// </summary>
    public struct Position
    {
        /// <summary>
        /// Position of unit
        /// </summary>
        /// <param name="line">line number</param>
        /// <param name="col">column number</param>
        public Position(long line,int col)
        {
            Line = line;
            Col = col;
        }
        /// <summary>
        /// line number
        /// </summary>
        public long Line { get; }
        /// <summary>
        /// column number
        /// </summary>
        public int Col { get; }
    }
}
