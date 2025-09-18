# Generated from DSDSL.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,18,110,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,1,0,5,0,24,8,0,10,0,12,0,27,
        9,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,39,8,1,1,2,1,2,1,
        2,1,2,3,2,45,8,2,1,3,1,3,1,3,1,3,3,3,51,8,3,1,4,1,4,1,4,1,4,1,4,
        1,4,5,4,59,8,4,10,4,12,4,62,9,4,1,4,1,4,3,4,66,8,4,1,5,1,5,1,5,3,
        5,71,8,5,1,5,3,5,74,8,5,1,6,1,6,1,6,1,6,3,6,80,8,6,1,7,1,7,1,7,1,
        7,3,7,86,8,7,1,7,3,7,89,8,7,1,8,1,8,1,8,1,8,3,8,95,8,8,1,8,3,8,98,
        8,8,1,9,1,9,1,9,5,9,103,8,9,10,9,12,9,106,9,9,1,10,1,10,1,10,0,0,
        11,0,2,4,6,8,10,12,14,16,18,20,0,1,1,0,13,15,118,0,25,1,0,0,0,2,
        38,1,0,0,0,4,40,1,0,0,0,6,46,1,0,0,0,8,52,1,0,0,0,10,67,1,0,0,0,
        12,75,1,0,0,0,14,81,1,0,0,0,16,90,1,0,0,0,18,99,1,0,0,0,20,107,1,
        0,0,0,22,24,3,2,1,0,23,22,1,0,0,0,24,27,1,0,0,0,25,23,1,0,0,0,25,
        26,1,0,0,0,26,28,1,0,0,0,27,25,1,0,0,0,28,29,5,0,0,1,29,1,1,0,0,
        0,30,39,3,4,2,0,31,39,3,6,3,0,32,39,3,8,4,0,33,39,3,10,5,0,34,39,
        3,12,6,0,35,39,3,14,7,0,36,39,3,16,8,0,37,39,5,17,0,0,38,30,1,0,
        0,0,38,31,1,0,0,0,38,32,1,0,0,0,38,33,1,0,0,0,38,34,1,0,0,0,38,35,
        1,0,0,0,38,36,1,0,0,0,38,37,1,0,0,0,39,3,1,0,0,0,40,41,5,1,0,0,41,
        42,5,14,0,0,42,44,5,14,0,0,43,45,5,2,0,0,44,43,1,0,0,0,44,45,1,0,
        0,0,45,5,1,0,0,0,46,47,5,3,0,0,47,48,5,14,0,0,48,50,3,18,9,0,49,
        51,5,2,0,0,50,49,1,0,0,0,50,51,1,0,0,0,51,7,1,0,0,0,52,53,5,4,0,
        0,53,54,5,14,0,0,54,55,5,5,0,0,55,60,3,20,10,0,56,57,5,6,0,0,57,
        59,3,20,10,0,58,56,1,0,0,0,59,62,1,0,0,0,60,58,1,0,0,0,60,61,1,0,
        0,0,61,63,1,0,0,0,62,60,1,0,0,0,63,65,5,7,0,0,64,66,5,2,0,0,65,64,
        1,0,0,0,65,66,1,0,0,0,66,9,1,0,0,0,67,68,5,8,0,0,68,70,5,14,0,0,
        69,71,5,14,0,0,70,69,1,0,0,0,70,71,1,0,0,0,71,73,1,0,0,0,72,74,5,
        2,0,0,73,72,1,0,0,0,73,74,1,0,0,0,74,11,1,0,0,0,75,76,5,9,0,0,76,
        77,5,14,0,0,77,79,5,16,0,0,78,80,5,2,0,0,79,78,1,0,0,0,79,80,1,0,
        0,0,80,13,1,0,0,0,81,82,5,10,0,0,82,85,5,16,0,0,83,84,5,11,0,0,84,
        86,5,14,0,0,85,83,1,0,0,0,85,86,1,0,0,0,86,88,1,0,0,0,87,89,5,2,
        0,0,88,87,1,0,0,0,88,89,1,0,0,0,89,15,1,0,0,0,90,91,5,12,0,0,91,
        92,5,14,0,0,92,94,5,14,0,0,93,95,3,18,9,0,94,93,1,0,0,0,94,95,1,
        0,0,0,95,97,1,0,0,0,96,98,5,2,0,0,97,96,1,0,0,0,97,98,1,0,0,0,98,
        17,1,0,0,0,99,104,3,20,10,0,100,101,5,6,0,0,101,103,3,20,10,0,102,
        100,1,0,0,0,103,106,1,0,0,0,104,102,1,0,0,0,104,105,1,0,0,0,105,
        19,1,0,0,0,106,104,1,0,0,0,107,108,7,0,0,0,108,21,1,0,0,0,14,25,
        38,44,50,60,65,70,73,79,85,88,94,97,104
    ]

class DSDSLParser ( Parser ):

    grammarFileName = "DSDSL.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'create'", "';'", "'insert'", "'build_tree'", 
                     "'['", "','", "']'", "'visualize'", "'save'", "'load'", 
                     "'as'", "'step'", "'#'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "ID", "NUMBER", "STRING", 
                      "COMMENT", "WS" ]

    RULE_script = 0
    RULE_statement = 1
    RULE_createStmt = 2
    RULE_insertStmt = 3
    RULE_buildTreeStmt = 4
    RULE_visualizeStmt = 5
    RULE_saveStmt = 6
    RULE_loadStmt = 7
    RULE_stepStmt = 8
    RULE_valueList = 9
    RULE_value = 10

    ruleNames =  [ "script", "statement", "createStmt", "insertStmt", "buildTreeStmt", 
                   "visualizeStmt", "saveStmt", "loadStmt", "stepStmt", 
                   "valueList", "value" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    ID=14
    NUMBER=15
    STRING=16
    COMMENT=17
    WS=18

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ScriptContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(DSDSLParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(DSDSLParser.StatementContext)
            else:
                return self.getTypedRuleContext(DSDSLParser.StatementContext,i)


        def getRuleIndex(self):
            return DSDSLParser.RULE_script

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterScript" ):
                listener.enterScript(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitScript" ):
                listener.exitScript(self)




    def script(self):

        localctx = DSDSLParser.ScriptContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_script)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 136986) != 0):
                self.state = 22
                self.statement()
                self.state = 27
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 28
            self.match(DSDSLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def createStmt(self):
            return self.getTypedRuleContext(DSDSLParser.CreateStmtContext,0)


        def insertStmt(self):
            return self.getTypedRuleContext(DSDSLParser.InsertStmtContext,0)


        def buildTreeStmt(self):
            return self.getTypedRuleContext(DSDSLParser.BuildTreeStmtContext,0)


        def visualizeStmt(self):
            return self.getTypedRuleContext(DSDSLParser.VisualizeStmtContext,0)


        def saveStmt(self):
            return self.getTypedRuleContext(DSDSLParser.SaveStmtContext,0)


        def loadStmt(self):
            return self.getTypedRuleContext(DSDSLParser.LoadStmtContext,0)


        def stepStmt(self):
            return self.getTypedRuleContext(DSDSLParser.StepStmtContext,0)


        def COMMENT(self):
            return self.getToken(DSDSLParser.COMMENT, 0)

        def getRuleIndex(self):
            return DSDSLParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)




    def statement(self):

        localctx = DSDSLParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 38
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 30
                self.createStmt()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 31
                self.insertStmt()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 3)
                self.state = 32
                self.buildTreeStmt()
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 4)
                self.state = 33
                self.visualizeStmt()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 5)
                self.state = 34
                self.saveStmt()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 6)
                self.state = 35
                self.loadStmt()
                pass
            elif token in [12]:
                self.enterOuterAlt(localctx, 7)
                self.state = 36
                self.stepStmt()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 8)
                self.state = 37
                self.match(DSDSLParser.COMMENT)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CreateStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(DSDSLParser.ID)
            else:
                return self.getToken(DSDSLParser.ID, i)

        def getRuleIndex(self):
            return DSDSLParser.RULE_createStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCreateStmt" ):
                listener.enterCreateStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCreateStmt" ):
                listener.exitCreateStmt(self)




    def createStmt(self):

        localctx = DSDSLParser.CreateStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_createStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self.match(DSDSLParser.T__0)
            self.state = 41
            self.match(DSDSLParser.ID)
            self.state = 42
            self.match(DSDSLParser.ID)
            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 43
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InsertStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(DSDSLParser.ID, 0)

        def valueList(self):
            return self.getTypedRuleContext(DSDSLParser.ValueListContext,0)


        def getRuleIndex(self):
            return DSDSLParser.RULE_insertStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInsertStmt" ):
                listener.enterInsertStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInsertStmt" ):
                listener.exitInsertStmt(self)




    def insertStmt(self):

        localctx = DSDSLParser.InsertStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_insertStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            self.match(DSDSLParser.T__2)
            self.state = 47
            self.match(DSDSLParser.ID)
            self.state = 48
            self.valueList()
            self.state = 50
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 49
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BuildTreeStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(DSDSLParser.ID, 0)

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(DSDSLParser.ValueContext)
            else:
                return self.getTypedRuleContext(DSDSLParser.ValueContext,i)


        def getRuleIndex(self):
            return DSDSLParser.RULE_buildTreeStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBuildTreeStmt" ):
                listener.enterBuildTreeStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBuildTreeStmt" ):
                listener.exitBuildTreeStmt(self)




    def buildTreeStmt(self):

        localctx = DSDSLParser.BuildTreeStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_buildTreeStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.match(DSDSLParser.T__3)
            self.state = 53
            self.match(DSDSLParser.ID)
            self.state = 54
            self.match(DSDSLParser.T__4)
            self.state = 55
            self.value()
            self.state = 60
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 56
                self.match(DSDSLParser.T__5)
                self.state = 57
                self.value()
                self.state = 62
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 63
            self.match(DSDSLParser.T__6)
            self.state = 65
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 64
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VisualizeStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(DSDSLParser.ID)
            else:
                return self.getToken(DSDSLParser.ID, i)

        def getRuleIndex(self):
            return DSDSLParser.RULE_visualizeStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVisualizeStmt" ):
                listener.enterVisualizeStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVisualizeStmt" ):
                listener.exitVisualizeStmt(self)




    def visualizeStmt(self):

        localctx = DSDSLParser.VisualizeStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_visualizeStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(DSDSLParser.T__7)
            self.state = 68
            self.match(DSDSLParser.ID)
            self.state = 70
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 69
                self.match(DSDSLParser.ID)


            self.state = 73
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 72
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SaveStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(DSDSLParser.ID, 0)

        def STRING(self):
            return self.getToken(DSDSLParser.STRING, 0)

        def getRuleIndex(self):
            return DSDSLParser.RULE_saveStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSaveStmt" ):
                listener.enterSaveStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSaveStmt" ):
                listener.exitSaveStmt(self)




    def saveStmt(self):

        localctx = DSDSLParser.SaveStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_saveStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75
            self.match(DSDSLParser.T__8)
            self.state = 76
            self.match(DSDSLParser.ID)
            self.state = 77
            self.match(DSDSLParser.STRING)
            self.state = 79
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 78
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoadStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(DSDSLParser.STRING, 0)

        def ID(self):
            return self.getToken(DSDSLParser.ID, 0)

        def getRuleIndex(self):
            return DSDSLParser.RULE_loadStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLoadStmt" ):
                listener.enterLoadStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLoadStmt" ):
                listener.exitLoadStmt(self)




    def loadStmt(self):

        localctx = DSDSLParser.LoadStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_loadStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.match(DSDSLParser.T__9)
            self.state = 82
            self.match(DSDSLParser.STRING)
            self.state = 85
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==11:
                self.state = 83
                self.match(DSDSLParser.T__10)
                self.state = 84
                self.match(DSDSLParser.ID)


            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 87
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StepStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(DSDSLParser.ID)
            else:
                return self.getToken(DSDSLParser.ID, i)

        def valueList(self):
            return self.getTypedRuleContext(DSDSLParser.ValueListContext,0)


        def getRuleIndex(self):
            return DSDSLParser.RULE_stepStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStepStmt" ):
                listener.enterStepStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStepStmt" ):
                listener.exitStepStmt(self)




    def stepStmt(self):

        localctx = DSDSLParser.StepStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_stepStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 90
            self.match(DSDSLParser.T__11)
            self.state = 91
            self.match(DSDSLParser.ID)
            self.state = 92
            self.match(DSDSLParser.ID)
            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 57344) != 0):
                self.state = 93
                self.valueList()


            self.state = 97
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 96
                self.match(DSDSLParser.T__1)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(DSDSLParser.ValueContext)
            else:
                return self.getTypedRuleContext(DSDSLParser.ValueContext,i)


        def getRuleIndex(self):
            return DSDSLParser.RULE_valueList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValueList" ):
                listener.enterValueList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValueList" ):
                listener.exitValueList(self)




    def valueList(self):

        localctx = DSDSLParser.ValueListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_valueList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 99
            self.value()
            self.state = 104
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 100
                self.match(DSDSLParser.T__5)
                self.state = 101
                self.value()
                self.state = 106
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(DSDSLParser.NUMBER, 0)

        def ID(self):
            return self.getToken(DSDSLParser.ID, 0)

        def getRuleIndex(self):
            return DSDSLParser.RULE_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue" ):
                listener.enterValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue" ):
                listener.exitValue(self)




    def value(self):

        localctx = DSDSLParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 107
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 57344) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





