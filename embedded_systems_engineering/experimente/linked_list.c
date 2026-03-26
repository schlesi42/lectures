#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
} LinkedList;

LinkedList* create_list() {
    LinkedList* list = (LinkedList*)malloc(sizeof(LinkedList));
    list->head = NULL;
    return list;
}

Node* create_node(int data) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->data = data;
    node->next = NULL;
    return node;
}

void insert_head(LinkedList* list, int data) {
    Node* node = create_node(data);
    node->next = list->head;
    list->head = node;
}

void insert_tail(LinkedList* list, int data) {
    Node* node = create_node(data);
    if (list->head == NULL) {
        list->head = node;
        return;
    }
    Node* current = list->head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = node;
}

void delete_node(LinkedList* list, int data) {
    if (list->head == NULL) return;
    
    if (list->head->data == data) {
        Node* temp = list->head;
        list->head = list->head->next;
        free(temp);
        return;
    }
    
    Node* current = list->head;
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

void print_list(LinkedList* list) {
    Node* current = list->head;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
}

void free_list(LinkedList* list) {
    Node* current = list->head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
    free(list);
}

int main() {
    LinkedList* list = create_list();
    insert_tail(list, 10);
    insert_tail(list, 20);
    insert_tail(list, 30);
    insert_head(list, 5);
    
    print_list(list);
    
    delete_node(list, 20);
    print_list(list);
    
    free_list(list);
    return 0;
}