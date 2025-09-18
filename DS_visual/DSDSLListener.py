# Generated from DSDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .DSDSLParser import DSDSLParser
else:
    from DSDSLParser import DSDSLParser

# This class defines a complete listener for a parse tree produced by DSDSLParser.
class DSDSLListener(ParseTreeListener):

    # Enter a parse tree produced by DSDSLParser#script.
    def enterScript(self, ctx:DSDSLParser.ScriptContext):
        pass

    # Exit a parse tree produced by DSDSLParser#script.
    def exitScript(self, ctx:DSDSLParser.ScriptContext):
        pass


    # Enter a parse tree produced by DSDSLParser#statement.
    def enterStatement(self, ctx:DSDSLParser.StatementContext):
        pass

    # Exit a parse tree produced by DSDSLParser#statement.
    def exitStatement(self, ctx:DSDSLParser.StatementContext):
        pass


    # Enter a parse tree produced by DSDSLParser#createStmt.
    def enterCreateStmt(self, ctx:DSDSLParser.CreateStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#createStmt.
    def exitCreateStmt(self, ctx:DSDSLParser.CreateStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#insertStmt.
    def enterInsertStmt(self, ctx:DSDSLParser.InsertStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#insertStmt.
    def exitInsertStmt(self, ctx:DSDSLParser.InsertStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#buildTreeStmt.
    def enterBuildTreeStmt(self, ctx:DSDSLParser.BuildTreeStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#buildTreeStmt.
    def exitBuildTreeStmt(self, ctx:DSDSLParser.BuildTreeStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#visualizeStmt.
    def enterVisualizeStmt(self, ctx:DSDSLParser.VisualizeStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#visualizeStmt.
    def exitVisualizeStmt(self, ctx:DSDSLParser.VisualizeStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#saveStmt.
    def enterSaveStmt(self, ctx:DSDSLParser.SaveStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#saveStmt.
    def exitSaveStmt(self, ctx:DSDSLParser.SaveStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#loadStmt.
    def enterLoadStmt(self, ctx:DSDSLParser.LoadStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#loadStmt.
    def exitLoadStmt(self, ctx:DSDSLParser.LoadStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#stepStmt.
    def enterStepStmt(self, ctx:DSDSLParser.StepStmtContext):
        pass

    # Exit a parse tree produced by DSDSLParser#stepStmt.
    def exitStepStmt(self, ctx:DSDSLParser.StepStmtContext):
        pass


    # Enter a parse tree produced by DSDSLParser#valueList.
    def enterValueList(self, ctx:DSDSLParser.ValueListContext):
        pass

    # Exit a parse tree produced by DSDSLParser#valueList.
    def exitValueList(self, ctx:DSDSLParser.ValueListContext):
        pass


    # Enter a parse tree produced by DSDSLParser#value.
    def enterValue(self, ctx:DSDSLParser.ValueContext):
        pass

    # Exit a parse tree produced by DSDSLParser#value.
    def exitValue(self, ctx:DSDSLParser.ValueContext):
        pass



del DSDSLParser