// Placeholder grammar for PDL v3.0 (YAML-based)
grammar PDLv3;

process: 'process' ':' NAME 'steps' ':' step+ EOF;

step: '-' 'id' ':' NAME 'type' ':' NAME ('actor' ':' NAME)? ('next' ':' NAME)?;

NAME: [a-zA-Z_][a-zA-Z_0-9-]*;
WS: [ \t\r\n]+ -> skip;
