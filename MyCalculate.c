#include <stdio.h>
#include <ctype.h>//pour verifie mes nombres
int main()
{
    float nombre_1,nombre_2;
    char operateur; //Empeche l'ecriture de plusieurs caractere a la suite
        
        printf("Veuillez choisir l'operateur de calcul entre +,-,/,* : \n");//Prend l'operateur pour effectuer le calacul
           scanf(" %c",&operateur);// ici espace de consummation de caractere indesirable +

        printf("Veuillez choisir le premier nombre :\n");
            scanf("%f",&nombre_1);//Prend l'entrer pour insert de val sur la var nombre_1
        
        printf("Veuillez choisir le second nombre \n (pour rappel le premier nombre et %f\n) ",nombre_1);
            scanf("%f",&nombre_2); //Prend l'entrer pour insert de val sur la var nombre_2
        
        
    
    if (nombre_2 == 0 && operateur == '/')
    {
        printf("Impossible");
    }else if (operateur != '+' && operateur != '-' && operateur != '*' && operateur != '/')
    {
       printf("Veuillez choisir un operateur valable entre + * / -"); 
    }else if(!isdigit (nombre_1) || !isdigit (nombre_2))//ici verification des caractere avec !isdigit alimmenter par #include <ctype.h>
    {
        printf("veuillez inserer un nombre de 0 a 9 ou une combinaison de nombre");
    }
    
    else{
         switch(operateur)
    {
        case '+':
            printf("Le resultat est %f ",nombre_1 + nombre_2);
        break;
        
        case '-':
            printf("Le resultat est %f",nombre_1 - nombre_2);
        break;
        
        case '/':
            printf("Le resultat est %f",nombre_1 / nombre_2);
        break;

        case '*':
            printf("Le resultat est %f",nombre_1 * nombre_2);
        break;
      }
    }   
return(0);
}
