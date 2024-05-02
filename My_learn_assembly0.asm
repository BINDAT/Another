section .data
  hello:db "Hi Mom!", 10 ;affiche un string
  helloLen: equ $-hello  ;compte les cara de string

section .text
  global _start ;entrer d'un point pour le lien

  _start:  ;start ici
    mov rax,1  ; sys_write (linux ici)
    mov rdi,1  ; stdout  (standard ici)
    mov rsi,hello  ; ecrit le message
    mov  rdx,helloLen  ; compte cara du string du message
    syscall  ;appel le noyau

  ; end program
  mov  rax,60  ; sys_exit  (sortie du programme)
  mov  rdi,0   ; error code 0 (success) (appel du code d'erreur 0 pour simplement dire que cela sais bien terminer)
  syscall  ;appel noyau
