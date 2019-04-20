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
using System.Text;
using System.Threading.Tasks;

namespace CompilerFramework.Parser
{
    /// <summary>
    /// The very base framework of parsing, provide very base methods for all kind of parsing.
    /// </summary>
    class ParserFramework
    {
        /// <summary>
        /// For the async multi-thread parsing order chacking.
        /// </summary>
        protected ParseDoor door = new ParseDoor();
        /// <summary>
        /// For the parsing order chacking.
        /// </summary>
        protected long index = 0;
        /// <summary>
        /// stack for PDA
        /// </summary>
        protected Stack<object> stack;
        /// <summary>
        /// parsing entrance methods
        /// </summary>
        /// <param name="parseUnit">parse unit</param>
        protected virtual void Parse(ParseUnit parseUnit) { }
        #region receive result of lexing
        /// <summary>
        /// Receive LexerResult and Parse synchronously, order of Index will be check.
        /// </summary>
        /// <param name="lexerResult">The Result of Lexer</param>
        public void ParseLexUnit(LexerResult lexerResult)
        {
            //check the order
            if (lexerResult.Index != index) throw new ParseIndexException(index, lexerResult.Index,
                "Index Error: Index should be " + index + " instead of " + lexerResult.Index);
            //transfer to parse unit
            ParseUnit parseUnit = new ParseUnit(lexerResult.Name, null, lexerResult.Position, lexerResult.Value, null);
            //to parse it
            index++;// move to next for sync
            door.GetIn();// move to next for async, but no use in here.
            Parse(parseUnit);
        }
        /// <summary>
        /// Receive LexerResult and Parse asynchronously, order of Index will be checked.
        /// </summary>
        /// <param name="lexerResult">The Result of Lexer</param>
        public async Task ParseLexUnitAsync(LexerResult lexerResult)
        {
            //check the order
            if (lexerResult.Index != index) throw new ParseIndexException(index, lexerResult.Index,
                "Index Error: Index should be " + index + " instead of " + lexerResult.Index);
            //transfer to parse unit
            ParseUnit parseUnit = new ParseUnit(lexerResult.Name, null, lexerResult.Position, lexerResult.Value, null);
            //to parse it
            index++;// move to next for sync
            await JoinParse(parseUnit, lexerResult.Index);
        }
        protected Task JoinParse(ParseUnit parseUnit, long index)
        {
            Task task = new Task(new Action<object>(x => Parse((ParseUnit)x)), parseUnit);
            while (door.Index < index) { }
            if (door.Index == index)
            {
                lock (door)
                {
                    door.GetIn();// move to next for async
                    task.RunSynchronously();// run it exclusively
                }
            }
            else
            {
                throw new AsyncIndexException(index,door.Index,
                "Async Index Error: Async Index should be " + index + " instead of " + door.Index+". Check your code please.");
            }
            return task;
        }
        #endregion
    }
    public struct ParseUnit
    {
        /// <summary>
        /// Unit of Parse, such as phrase.
        /// </summary>
        /// <param name="name">name of this, such as "class"</param>
        /// <param name="parseUnits">the unit contained, as son nodes</param>
        /// <param name="value">reserved place for advanced usage</param>
        /// <param name="property">reserved place for advanced usage</param>
        /// <param name="position">position of unit</param>
        public ParseUnit(string name, ParseUnit[] parseUnits, Position position, object value, object property)
        {
            Name = name;
            ParseUnits = parseUnits;
            Value = value;
            Position = position;
            Property = property;
        }
        /// <summary>
        /// name of this
        /// </summary>
        public string Name { get; private set; }
        /// <summary>
        /// the unit contained, as son nodes
        /// </summary>
        public ParseUnit[] ParseUnits { get; private set; }
        /// <summary>
        /// reserved place for advanced usage
        /// </summary>
        public object Value { get; private set; }
        /// <summary>
        /// position of unit
        /// </summary>
        public Position Position { get; }
        /// <summary>
        /// reserved place for advanced usage
        /// </summary>
        public object Property { get; }
    }
    /// <summary>
    /// Exception when index is not match
    /// </summary>
    public class ParseIndexException:Exception
    {
        /// <summary>
        /// Exception when index is not match
        /// </summary>
        /// <param name="corIndex">index should be</param>
        /// <param name="errIndex">current index</param>
        /// <param name="message">message of exception</param>
        public ParseIndexException(long corIndex,long errIndex,string message) : base(message)
        {
            CorIndex = corIndex;
            ErrIndex = errIndex;
        }
        /// <summary>
        /// index should be
        /// </summary>
        public long CorIndex { get; }
        /// <summary>
        /// current index
        /// </summary>
        public long ErrIndex { get; }
    }
    /// <summary>
    /// For async multi-thread operation to lock it
    /// </summary>
    internal class ParseDoor
    {
        /// <summary>
        /// which index should to lock next
        /// </summary>
        internal long Index { get; private set; } = 0;
        /// <summary>
        /// get in door and lock this object, lock operation should be done by you outside.
        /// </summary>
        internal void GetIn() => Index++;
    }
    /// <summary>
    /// Exception when async index is bigger than current index, generally this will not happen if no coding error.
    /// </summary>
    public class AsyncIndexException : Exception
    {
        /// <summary>
        /// Exception when async index is bigger than current index, generally this will not happen if no coding error.
        /// </summary>
        /// <param name="curIndex">current index</param>
        /// <param name="errIndex">error async index</param>
        /// <param name="message">message of exception</param>
        public AsyncIndexException(long curIndex, long errIndex, string message) : base(message)
        {
            CurIndex = curIndex;
            ErrIndex = errIndex;
        }
        /// <summary>
        /// current index
        /// </summary>
        public long CurIndex { get; }
        /// <summary>
        /// error async index
        /// </summary>
        public long ErrIndex { get; }
    }
}
