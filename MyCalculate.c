#include <stdio.h>
int main()
{
    float nombre_1,nombre_2;
    char operateur;
        
        printf("Veuillez choisir le premier nombre :\n");
            scanf("%f",&nombre_1);//Prend l'entrer pour insert de val sur la var nombre_1
        
        printf("Veuillez choisir le second nombre \n (pour rappel le premier nombre et %f\n :) \n:",nombre_1);
            scanf("%f",&nombre_2); //Prend l'entrer pour insert de val sur la var nombre_2
        
        printf("Veuillez choisir l'operateur de calcul entre +,-,/,* : \n");//Prend l'operateur pour effectuer le calacul
           scanf(" %c",&operateur);// ici espace de consummation de caractere indesirable 
    
    if (nombre_2 == 0 && operateur == '/')
    {
        printf("Impossible");
    }else{
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
