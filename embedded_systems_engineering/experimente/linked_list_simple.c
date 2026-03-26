#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

/* Hilfsfunktion */
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
void insert_head(Node** head, int data) {
    Node* node = create_node(data);
    node->next = *head;
    *head = node;
}

/* Insert am Ende */
void insert_tail(Node** head, int data) {
    Node* node = create_node(data);

    if (*head == NULL) {
        *head = node;
        return;
    }

    Node* current = *head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = node;
}

/* Löschen eines Elements */
void delete_node(Node** head, int data) {
    if (*head == NULL) return;

    /* Spezialfall: erstes Element löschen */
    if ((*head)->data == data) {
        Node* temp = *head;
        *head = (*head)->next;
        free(temp);
        return;
    }

    Node* current = *head;
    while (current->next != NULL) {
        if (current->next->data == data) {
            Node* temp = current->next;
            current->next = current->next->next;
            free(temp);
            return;
        }
        current = current->next;
    }
}

/* Ausgabe */
void print_list(Node* head) {
    Node* current = head;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
}

/* Speicher freigeben */
void free_list(Node** head) {
    Node* current = *head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
    *head = NULL;
}

int main() {
    Node* head = NULL;

    insert_tail(&head, 10);
    insert_tail(&head, 20);
    insert_tail(&head, 30);
    insert_head(&head, 5);

    print_list(head);

    delete_node(&head, 20);
    print_list(head);

    free_list(&head);

    return 0;
}