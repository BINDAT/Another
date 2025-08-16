#include <stdio.h> // Inclusion de la bibliothèque standard d'entrée/sortie
#include <stdlib.h> // Inclusion de la bibliothèque standard
#include <string.h> // Inclusion de la bibliothèque de chaînes de caractères

typedef struct id // Structure pour stocker l'identité d'une personne
{
    char primo[20]; // Prénom
    char nomfam[20]; // Nom de famille
}personne; // Fin de la structure personne

typedef struct date // Structure pour stocker une date
{
    int sjour; // Jour
    int smois; // Mois
    int sannee; // Année
}calendrier; // Fin de la structure calendrier

struct humain // Structure pour stocker les informations d'un humain
{
    personne hnom; // Informations sur l'identité
    calendrier hdatenaiss; // Informations sur la date de naissance
};

int main() // Fonction principale
{
    struct humain dev; // Déclaration de la variable dev de type humain
    printf("Votre Prénom \n"); // Demande du prénom
    scanf("%s",dev.hnom.primo); // Lecture du prénom
    printf("Votre Nom\n"); // Demande du nom
    scanf("%s",dev.hnom.nomfam); // Lecture du nom
    printf("Votre jour de naissance\n"); // Demande du jour de naissance
    scanf("%d",&dev.hdatenaiss.sjour); // Lecture du jour de naissance
    printf("Votre mois de naissance\n"); // Demande du mois de naissance
    scanf("%d",&dev.hdatenaiss.smois); // Lecture du mois de naissance
    printf("Votre année de naissance\n"); // Demande de l'année de naissance
    scanf("%d",&dev.hdatenaiss.sannee); // Lecture de l'année de naissance

    printf("Je suis %s %s\nné le %d/%d/%d\n",dev.hnom.primo,dev.hnom.nomfam,dev.hdatenaiss.sjour,dev.hdatenaiss.smois,dev.hdatenaiss.sannee); // Affichage des informations

    return(0); // Fin de la fonction principale
}