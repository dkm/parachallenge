grammar parachallenge;
options {
	output=AST;
//	backtrack=true;
//	memoize=true;
} 

tokens {
	DISTANCE;
	WPTS;
	WPT;
	TAKEOFF;
	LANDING;
	UTM_COORDS;
	DIFFICULTY;
}

ID  :	('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;

INT :	'0'..'9'+
    ;

FLOAT
    :   ('0'..'9')+ '.' ('0'..'9')*
    ;

COMMENT
    :   '//' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;}
    |   '/*' ( options {greedy=false;} : . )* '*/' {$channel=HIDDEN;}
    ;

WS  :   ( ' '
        | '\t'
        ) {$channel=HIDDEN;}
    ;

STRING
    :  '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

fragment
EXPONENT : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;

fragment
HEX_DIGIT : ('0'..'9'|'a'..'f'|'A'..'F') ;

fragment
ESC_SEQ
    :   '\\' ('b'|'t'|'n'|'f'|'r'|'\"'|'\''|'\\')
    |   UNICODE_ESC
    |   OCTAL_ESC
    ;

fragment
OCTAL_ESC
    :   '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7')
    ;

fragment
UNICODE_ESC
    :   '\\' 'u' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT
    ;


string_to_eol 
	:	 ( options {greedy=false;} : . )* '\n'! ;

title	:  string_to_eol;


subtitle 
	:	 string_to_eol;

distance:	'Kilometrage (hors bonus)' ':' INT? '\n' -> ^(DISTANCE INT?);

difficulty 
	:	 'Degre de difficulte' ':' INT? '\n' -> ^(DIFFICULTY INT?);

utm_coords
	:	(n=INT|n=FLOAT) 'N' (e=INT|e=FLOAT) 'E' t=INT'T'-> ^(UTM_COORDS $n $e $t);
	
takeoff	:	'Deco' ':' utm_coords string_to_eol -> ^(TAKEOFF utm_coords string_to_eol);

waypoint:	
	'-' utm_coords string_to_eol -> ^(WPT utm_coords string_to_eol);
	
waypoints
	:	'Balises' ':' '\n'
	        waypoint+
	        	-> ^(WPTS waypoint+)
	;

landing	:	'Atterro' ':' utm_coords string_to_eol -> ^(LANDING utm_coords);

fiche	:	
	title
	subtitle
	distance
	difficulty
	takeoff
	waypoints
	landing
	;
	