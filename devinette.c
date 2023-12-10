#include <stdio.h>
#define Trouve 99
int main()
{
    int search;
    printf("Trouvez le nombre : ");
    scanf("%d",&search);
    if(search != Trouve)
    {
        if(search > Trouve){
            printf("Non vous avez mentionner un nombre plus grand que celui a trouver");
        }
        else{
            printf("Non vous avez indiquer un nombre plus petit que celui a deviner");
        }
        return(0);
    }
    else {
        printf("Bravo vous avez trouver le bon nombre qui est bien %d",Trouve);
    }
    return(1);
}