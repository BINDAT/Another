#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct id
{
    char primo[20];
    char nomfam[20];
}personne;

typedef struct date
{
    int sjour;
    int smois;
    int sannee;
}calendrier;

struct humain
{
    personne hnom;
    calendrier hdatenaiss;
};

int main()
{
    struct humain dev;
    printf("Votre Prénom \n");
    scanf("%s",dev.hnom.primo);
    printf("Votre Nom\n");
    scanf("%s",dev.hnom.nomfam);
    printf("Votre jour de naissance");
    scanf("%d",&dev.hdatenaiss.sjour);
    printf("Votre mois de naissance");
    scanf("%d",&dev.hdatenaiss.smois);
    printf("Votre année de naissance");
    scanf("%d",&dev.hdatenaiss.sannee);
    
    printf("Je suis %s %s\nné le %d/%d/%d\n",dev.hnom.primo,dev.hnom.nomfam,dev.hdatenaiss.sjour,dev.hdatenaiss.smois,dev.hdatenaiss.sannee);

    return(0);
}