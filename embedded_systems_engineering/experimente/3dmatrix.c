#include <stdio.h>
#include <stdlib.h>

typedef struct IntNode {
    int data;
    struct IntNode* next;
} IntNode;

typedef struct RowNode {
    IntNode* row;
    struct RowNode* next;
} RowNode;

typedef struct {
    RowNode* rows;
} Matrix;

typedef struct MatrixNode {
    Matrix* matrix;
    struct MatrixNode* next;
} MatrixNode;

typedef struct {
    MatrixNode* matrices;
} Matrix3D;

Matrix* createMatrix(int rows, int cols) {
    Matrix* matrix = (Matrix*)malloc(sizeof(Matrix));
    matrix->rows = NULL;

    for (int i = 0; i < rows; i++) {
        RowNode* newRow = (RowNode*)malloc(sizeof(RowNode));
        newRow->row = NULL;
        newRow->next = matrix->rows;
        matrix->rows = newRow;

        for (int j = 0; j < cols; j++) {
            IntNode* newInt = (IntNode*)malloc(sizeof(IntNode));
            newInt->data = 0; // Initialize with 0
            newInt->next = newRow->row;
            newRow->row = newInt;
        }
    }

    return matrix;
}

Matrix3D* createMatrix3D(int depth, int rows, int cols) {
    Matrix3D* matrix3D = (Matrix3D*)malloc(sizeof(Matrix3D));
    matrix3D->matrices = NULL;

    for (int i = 0; i < depth; i++) {
        MatrixNode* newMatrixNode = (MatrixNode*)malloc(sizeof(MatrixNode));
        newMatrixNode->matrix = createMatrix(rows, cols);
        newMatrixNode->next = matrix3D->matrices;
        matrix3D->matrices = newMatrixNode;
    }

    return matrix3D;
}

void freeMatrix(Matrix* matrix) {
    RowNode* currentRow = matrix->rows;
    while (currentRow) {
        IntNode* currentInt = currentRow->row;
        while (currentInt) {
            IntNode* tempInt = currentInt;
            currentInt = currentInt->next;
            free(tempInt);
        }
        RowNode* tempRow = currentRow;
        currentRow = currentRow->next;
        free(tempRow);
    }
    free(matrix);
}

void freeMatrix3D(Matrix3D* matrix3D) {
    MatrixNode* currentMatrixNode = matrix3D->matrices;
    while (currentMatrixNode) {
        freeMatrix(currentMatrixNode->matrix);
        MatrixNode* tempMatrixNode = currentMatrixNode;
        currentMatrixNode = currentMatrixNode->next;
        free(tempMatrixNode);
    }
    free(matrix3D);
}

void printMatrix(Matrix* matrix) {
    RowNode* currentRow = matrix->rows;
    while (currentRow) {
        IntNode* currentInt = currentRow->row;
        while (currentInt) {
            printf("%d ", currentInt->data);
            currentInt = currentInt->next;
        }
        printf("\n");
        currentRow = currentRow->next;
    }
}

void printMatrix3D(Matrix3D* matrix3D) {
    MatrixNode* currentMatrixNode = matrix3D->matrices;
    int depth = 0;
    while (currentMatrixNode) {
        printf("Matrix at depth %d:\n", depth);
        printMatrix(currentMatrixNode->matrix);
        currentMatrixNode = currentMatrixNode->next;
        depth++;
    }
}

int main() {
    int depth = 2, rows = 3, cols = 4;
    Matrix3D* matrix3D = createMatrix3D(depth, rows, cols);

    // Example: Set some values in the first matrix
    MatrixNode* currentMatrixNode = matrix3D->matrices;
    if (currentMatrixNode) {
        RowNode* currentRow = currentMatrixNode->matrix->rows;
        for (int i = 0; i < rows && currentRow; i++) {
            IntNode* currentInt = currentRow->row;
            for (int j = 0; j < cols && currentInt; j++) {
                currentInt->data = i * cols + j + 1; // Fill with sample data
                currentInt = currentInt->next;
            }
            currentRow = currentRow->next;
        }
    }

    printMatrix3D(matrix3D);
    freeMatrix3D(matrix3D);
    return 0;
}