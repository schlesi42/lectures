#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* create_node(int data) {
    Node* node = malloc(sizeof(Node));
    if (!node) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    node->data = data;
    node->next = NULL;
    return node;
}

/* Insert am Kopf */
void insert_head(Node* head, int data) {
    Node* node = create_node(data);
    node->next = head;
    head = node;
}


int main() {
    Node* head = NULL;

    insert_head(head, 1);
    insert_head(head, 2);
    insert_head(head, 3);

    /* Ausgabe der Liste */
    Node* current = head;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");

    return 0;
}