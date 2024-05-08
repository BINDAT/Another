MOV AX, 7	; AX, qui est mis à 7, sera la destination
ADD AX, 6	; On ajoute à AX la valeur 6, le résultat étant stocké dans la destination, soit AX
MOV BX, 3	; On met dans BX la valeur 3 qui servira de source à la division
DIV BX		; DIV divise AX par la source, ici BX, qui vaut 3
;le résultat de la division est stocké dans la destination (BX)
;et le modulo (reste de la division qui nous intéresse ici) est mis dans DX
