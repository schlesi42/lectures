#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_THREADS 4

typedef struct {
    int id;
    int iterations;
} thread_args_t;

void *worker(void *arg) {
    thread_args_t *args = (thread_args_t *)arg;

    for (int i = 0; i < args->iterations; i++) {
        printf("[Thread %d] Schritt %d/%d\n", args->id, i + 1, args->iterations);
        usleep(1000000 + (rand() % 2000000)); 
    }

    printf("[Thread %d] Fertig!\n", args->id);
    return NULL;
}

int main(void) {
    pthread_t threads[NUM_THREADS];
    thread_args_t args[NUM_THREADS];

    printf("Starte %d Threads...\n\n", NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].id = i;
        args[i].iterations = 3 + (rand() % 4); // 3-6 Iterationen
        if (pthread_create(&threads[i], NULL, worker, &args[i]) != 0) {
            perror("pthread_create");
            return 1;
        }
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\nAlle Threads abgeschlossen.\n");
    return 0;
}
