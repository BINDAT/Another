#include <stdio.h>
#include <string.h>

int main()
{
    struct id
    {
        char prénom[20],nom[20],sexe[5];
        int jours,mois,année;
    }id;
    puts("Votre prénom : ");
    scanf("%s",id.prénom);
    puts("Votre nom : ");
    scanf("%s",id.nom);
    puts("Homme ou Femme ? :");
    scanf("%s",id.sexe);
    puts("Votre jours de naissance : ");
    scanf("%d",&id.jours);
    puts("Votre mois : ");
    scanf("%d",&id.mois);
    puts("Votre année : ");
    scanf("%d",&id.année);
    printf("Vous êtes %s %s est êtes un(e) %s vous êtes né(e) le %d %d %d",id.prénom,id.nom,id.sexe,id.jours,id.mois,id.année);
    return(0);
}