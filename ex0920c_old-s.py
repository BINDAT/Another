import sys

cmptr = 0
while True:
    sys.stdout.write(str(cmptr) + "\t")  # Utilisation de \t pour la tabulation
    cmptr = cmptr + 1
    if cmptr >= 50:
        break




#Bloc d'origine du programme en langage C
##include <stdio.h>

#int main()
#{
#    int cmptr;

#    cmptr = 0;
#    for (;;)
#    {
#        printf("%d, ", cmptr);
#        cmptr = cmptr +1;
#        if (cmptr > 50)
#        break;
#    }
#    putchar('\n');
#    return(0);
#}
#/*
#Obersavtion : Ici le programe compte jusqua 50 grace au if break cela est aussi une solution pour sortir d'une boucle infini
#boucle infini causer ici par sois while(1) ou la maintenant par for(;;)
#*/