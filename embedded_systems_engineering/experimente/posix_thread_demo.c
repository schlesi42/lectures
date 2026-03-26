#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
void* print_char (void* ch)
{
int i;
for (i=0;i< 10; i++) {
    printf ("%c", *(char*) ch);
    usleep(1000);
}
return NULL;
}
int main()
{
char ch1='-', ch2='*';
pthread_t p1, p2;
pthread_create(&p1, NULL, print_char ,&ch1);
pthread_create(&p2, NULL, print_char ,&ch2);
pthread_join(p1, NULL);
pthread_join(p2, NULL);
printf("\n");
return 0;
}