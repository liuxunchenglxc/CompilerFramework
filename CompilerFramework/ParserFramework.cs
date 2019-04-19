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

namespace CompilerFramework
{
    /// <summary>
    /// The very base framework of parsing, provide very base methods for all kind of parsing.
    /// </summary>
    class ParserFramework
    {
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
            //transfer to parse unit
            ParseUnit parseUnit = new ParseUnit(lexerResult.Name, null, lexerResult.Position, lexerResult.Value, null);
            //to parse it
            Parse(parseUnit);
        }
        public void ParseLexUnitBegin()
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
}
