#include <stdio.h> // Inclusion de la bibliothèque standard d'entrée/sortie
#include <string.h> // Inclusion de la bibliothèque de chaînes de caractères

int main() // Fonction principale
{
    struct id // Structure pour stocker l'identité d'une personne
    {
        char prénom[20],nom[20],sexe[5]; // Informations personnelles
        int jours,mois,année; // Date de naissance
    }id; // Fin de la structure id
    puts("Votre prénom : "); // Demande du prénom
    scanf("%s",id.prénom); // Lecture du prénom
    puts("Votre nom : "); // Demande du nom
    scanf("%s",id.nom); // Lecture du nom
    puts("Homme ou Femme ? :"); // Demande du sexe
    scanf("%s",id.sexe); // Lecture du sexe
    puts("Votre jours de naissance : "); // Demande du jour de naissance
    scanf("%d",&id.jours); // Lecture du jour de naissance
    puts("Votre mois : "); // Demande du mois
    scanf("%d",&id.mois); // Lecture du mois
    puts("Votre année : "); // Demande de l'année
    scanf("%d",&id.année); // Lecture de l'année
    printf("Vous êtes %s %s est êtes un(e) %s vous êtes né(e) le %d %d %d",id.prénom,id.nom,id.sexe,id.jours,id.mois,id.année); // Affichage des informations
    return(0); // Fin de la fonction principale
}