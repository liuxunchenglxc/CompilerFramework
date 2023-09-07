# CompilerFramework
一个具有完整词法分析与支持输入生成式的语法分析的编译器框架，支持在语法分析部分添加语义分析回调函数以利用语法分析的结果。

A Compiler Framework with complete lexical analysis and production supportted parsing analysis, which is supportted to add the callback funtion to parsing analysis for semantic analysis.

该框架具有Python 3与C#两个语言版本。C#版本开发于2019年并且已经停止维护。Python 3版本已经重现了C#版本的全部基础功能，并且更多功能正在添加中。

This framework has both Python 3 and C# versions. C# version has stopped maintenance. Python 3 version has included all essential functions in C# version, and more functions are incoming.

### Author's self-talking

现在(2023-09-02)，居然，Python的代码量和C#的差不多一样多了，看来这个仓库马上要变成Python仓库了，2333。

At present (2023-09-02), actually, the row number of Python is just almost same as C#'s. It seems that this repository is about to become Python repository,  lol.

(2023-09-07) 终于把LR(0)和LR(1)的测试都跑通了。作者也文档里添加了一个解析数学表达式的简单例子。

(2023-09-07) Eventually, both LR(0) and LR(1) are running successfully, and the author added an example of parsing math expressions in the docs.

# Python Version

- **开发人员**: `刘迅承`
- **Author**: `Xuncheng Liu`
- **开发语言**: `Python 3`
- **Programming Language**: `Python 3`
- **项目依赖**: 只有`Python标准库`
- **Dependence**: Only the `Python Standard Library`

## Schedule

### Done
- [x] LexerFramework class (Lexical Analysis base class)
- [x] HLlangLexerFramework class (Lexical Analysis high class)
- [x] Lexer Docs (Lexical Analysis)
- [x] ParserFramework (Parsing base class)
- [x] Parser Docs (Parsing)
- [x] LRParserFramework (Bottom-up parsing base class)
- [x] LR(0) and LR(1) Parser with operator priority (Bottom-up parsing high class)
- [x] LR(0) and LR(1) Unit Test and Bugfix (Bottom-up part)
### Doing
- [ ] SLR high class (Bottom-up parsing)
### Todo
- [ ] LALR(1) (Bottom-up parsing)
- [ ] Test Bottom-up Parser
- [ ] Top-down Parser Framework
- [ ] Something more...

## Docs
https://compilerframework.readthedocs.io/en/latest/index.html

## Docstring Format
Author uses the Numpy format as Sphinx docs shown.

https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html#example-numpy

# CSharp Version
作者现在写下面这句话的时候是2023年。这个C#版本是2019年写的，现在4年过去了，由于作者的电脑里也早就没有了那些开发环境，C#也很久没有碰过了，并且最近一直在使用Python，所以C#版本大概率不会再更新，相反，作者会新写一个Python版本来替代原来的版本，毕竟作者个人认为最终编译器的实现并不在于框架使用了什么语言，框架只是为了方便大家去设计词法语法等这些基础的东西，大家可以借助框架来生成C语言片段甚至汇编语言片段等底层语言来帮助实现最终的语义部分，以形成编译器成品。

- **开发人员**: `刘迅承`
- **依赖环境**: `.NET Core 2.1`
- **开发环境**: `Visual Studio 2017`
- **开发语言**: `C# 7.1`
- **命名空间**: `CompilerFramework`
- **详细参考**: `./CompilerFramework/CompilerFramework.xml`

## 词法部分：

**命名空间**：`CompilerFramework.Lexer`

**基本原理**：正则表达式/确定性有穷自动机DFA

**层次结构**：基础功能 -> 高级功能封装

### 基础框架类：`LexerFramework`

- **基本功能**：实现正则表达式与词法分析的桥梁。
- **基本应用**：对普通的语言进行基本的词法分析。
- **高级功能**：实现多组正则表达式分组匹配模式。
- **高级应用**：对多行注释实现词法分析，构建多重匹配分支与入口。
- **应用步骤**：先添加`LexItem`再对`TextReader`进行词法分析。
- **词法分析方式**：逐行读入逐行分析，单次匹配触发事件，持续分析。
- **词法分析结果**：从事件`OnLexedEventHandler`接收结果，并可以根据结果更改匹配组，以实现改变匹配分支。
- **词法分析异常**：
  1. 匹配组号超出预定组号，报告组号，异常类为`GroupNumException`
  2. 匹配失败，报告失败位置，异常类为`NoMatchException`
  3. 零长度匹配，会引起死循环，报告具体的`LexItem`内容，异常类为`ZeroLenghtMatchException`
  4. 词法项名称非法，比如以`@`开头，报告具体的名称，异常类为`IlleagalNameException`
- **词法分析最小单位**：结构体`LexItem`
  1. 名称：便于语法分析与分类
  2. 正则表达式：匹配法则，自动在表达式最前方添加`^`
  3. 正则表达式匹配模式：默认不使用特殊模式
  4. 匹配结果文本处理委托：用于对文本结果的处理
- **词法分析结果最小单位**：结构体`LexerResult`
  1. 次序：便于计次与异步处理
  2. 名称：与结构体`LexItem`的名称一致
  3. 值：经过用户处理后或默认`string`内容不变，类型为`object`的结果
  4. 位置：词法项出现的位置，用于下一步语法分析的报错信息等。
- **词法分析计数方式**：根据事件返回值判断是否计数，如果返回真则计数，且判定为“接受的结果”，可送入语法分析。特别的，如果匹配结果经过处理后为空，则不触发事件，不计数。
- **输入流**：输入选择`TextReader`类，其派生类`StringReader`可接收字符串流，`StreamReader`可接收文件流。适配最常用的两种输入类型。
- **语法分析桥梁**：事件`OnAcceptedEventHandler`，其中的`LexerResult`均为“接受的结果”，并已经按顺序连续计数。在此事件中请调用语法分析相关函数，比如`ParseLexUnit`或`ParseLexUnitAsync`。
- **语法分析结束**：方法`LexStream`返回值即为“接受的结果”的总数，可以作为语法分析中词法分析结果传入结束标志的组成之一，并在方法返回后调用相关函数以告知语法分析部分传入结束了。此外，事件`OnFinishedEventHandler`同样提供了“接受的结果”的总数，并可以调用相关函数以通知语法分析部分。两种方法皆可。

### 派生框架类：`HLlangLexerFramework`

- **基本功能**：封装高级编程语言的词法分析项
- **基本应用**：更容易，代码更少的创建词法分析器
- **高级功能**：分组匹配时，匹配组的批量添加
- **高级应用**：更容易，代码更少的实现多组匹配词法分析器
- **词法分析封装**：
  1. **添加保留字**：批量添加，自动在正则表达式末尾添加零宽断言`(?=\W|$)`
  2. **添加标识符**：默认规则为`[A-Za-z]\w*`
  3. **添加运算符**：批量添加，无特殊处理
  4. **添加界符**：批量添加，无特殊处理
  5. **添加常项**：批量添加，可选自动在正则表达式末尾添加零宽断言`(?=\W|$)`
  6. **常用转换委托**

## 语法部分：

**命名空间**：`CompilerFramework.Parser`

**基本原理**：上下文无关文法CFG/下推自动机PDA

**层次结构**：

- 基础框架 -> 自顶向下、自底向上文法
- 自顶向下 -> LL(1)文法
- 自底向上 -> LR(0) -> SLR(1) -> LR(1) -> LALR(1)文法

### 基础框架类：`ParserFramework`

- **构建目的**：通过定义最基本的语法分析框架，形成统一的语法分析接口与规范。
- **基本功能**：实现词法分析结果与语法分析的桥梁，并实现最基本的语法分析框架定义。
- **基本应用**：通过对此类的派生，对普通语言的词法分析结果进行基本的语法分析。
- **基本机制**：逐个同步或异步读入，顺序放入分析器分析。
- **语法分析准备阶段**：
  - **同步方法**：`ParseLexUnit`，此方法会直到相关语法分析阶段性结束后（比如归约移进后，或预测表分析后）才返回，然后语法分析等待读入下一个词法分析结果。
  - **异步机制**：类`ParseDoor`专门用于控制多线程同步，此类中实例化为`door`对象。通过`door.Index`的判断与`lock (door)`配合来实现异步下的词法分析结果输入。
  - **异步方法**：`ParseLexUnitAsync`，此方法会将词法分析结果加入await关键字下的方法中，之后词法分析结果们会排队传入语法分析部分。具体排队方法为判断当前的`door.Index`是否等于自己的Index，如果小于则继续等待，如果等于则锁住`door`，开始语法分析。判断使用while循环，因为lock后会阻塞一切while判断，当阻塞消失时，只有相应的词法分析结果才能进入，这样既不会导致过多while判断而死掉，也不会带来额外的内存空间及其管理代码。
- **语法分析准备阶段异常**：
  1. （同步与异步）传入的词法分析结果不是按照顺序的。异步方法要求顺序调用，以保证不缺补漏。报告传入的词法分析结果的`Index`与应当传入的`Index`项，异常类为`ParseIndexException`。
  2. （异步）异步机制出现异常，应当进入语法分析的项没有进入，此异常一般情况下不应该发生，除非有代码逻辑错误。报告没有传入项的`Index`与欲接收的`Index`,异常类为`AsyncIndexException`。
- **语法分析产生式**：
  1. **结构体**：`Production`
     - Pre：`string`类型的前件，会作为新生成的语法分析单位的名称。
     - Sufs：`string[]`类型的后件，会匹配相应名称的语法单位。
     - SemantDelegate：语义分析委托，用于语义分析。
     - Attr：`object`类型的附加属性用于高级用途。
  2. **基本添加方法**：`AddProduction`，直接将`Production`结构体添入语法分析框架。
  3. **文本添加方法**：`AddProductionByString`，根据格式

      ``` c
      Pre -> Suf_0 Suf_1 ... [@SemantDelegateName[$attr]]
      Pre | Suf_0 Suf_1 ... [@SemantDelegateName[$attr]]
      Pre : Suf_0 Suf_1 ... [@SemantDelegateName[$attr]]
      ```

      添加字符串实参，比如`E -> F H @delegateName$attrString`。
      如果需要添加语义分析委托，请先调用`AddSemantDelegateTable`
      添加语义分析委托名称的映射。如果要使用`attr`，必须先使用语义分析委托。
  4. **批量添加方法**：`AddProductionsByStrings`，文本添加方法的批量方法。
  5. **异常**：`ProductSentenceException`，如果产生式文本格式错误，则抛出异常，并报告具体文本。
- **最小语法分析单位**：`ParseUnit`
  1. 创建规则：由词法分析结果或产生式创建，不可以由用户主动创建。
  2. Name：名称，与产生式前件或词法分析结果名称一致。
  3. ParseUnits：子单位们，以形成语法树。
  4. Position：语法项的位置，由第一个（最前端）的词法分析项位置决定。
  5. Property：为高级应用预留的位置。
  6. Value：保存的值，比如词法分析结果的值等。
