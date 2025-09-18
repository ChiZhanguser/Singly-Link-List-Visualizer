grammar DSDSL;

script: statement* EOF;

statement
  : createStmt
  | insertStmt
  | buildTreeStmt
  | visualizeStmt
  | saveStmt
  | loadStmt
  | stepStmt
  | COMMENT
  ;

createStmt: 'create' ID ID ';'? ;
insertStmt: 'insert' ID valueList ';'? ;
buildTreeStmt: 'build_tree' ID '[' value (',' value)* ']' ';'? ;
visualizeStmt: 'visualize' ID (ID)? ';'? ;
saveStmt: 'save' ID STRING ';'? ;
loadStmt: 'load' STRING ('as' ID)? ';'? ;
stepStmt: 'step' ID ID valueList? ';'? ;

valueList: value (',' value)* ;
value: NUMBER | ID | '#' ;

ID: [a-zA-Z_][a-zA-Z0-9_]* ;
NUMBER: '-'? [0-9]+ ('.' [0-9]+)? ;
STRING: '"' (~["\r\n])* '"' ;
COMMENT: '#' ~[\r\n]* -> skip ;
WS: [ \t\r\n]+ -> skip ;
