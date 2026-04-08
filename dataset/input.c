#include <stdio.h>
#include <stdlib.h>

// A simulated data processing suite
void run_analysis() {
    int dataset[12] = {10, 50, 30, 70, 80, 60, 20, 90, 40, 100, 11, 22};
    int total_elements = 12;
    int search_key = 60;

    // --- CASE 1: A nested bubble sort with different naming ---
    printf("Sorting dataset...\n");
    for (int p = 0; p < total_elements - 1; p++) {
        for (int q = 0; q < total_elements - p - 1; q++) {
            if (dataset[q] > dataset[q + 1]) {
                int swap = dataset[q];
                dataset[q] = dataset[q + 1];
                dataset[q + 1] = swap;
            }
        }
    }

    // --- CASE 2: A standard linear search ---
    printf("Searching for key...\n");
    int position = -1;
    for (int i = 0; i < total_elements; i++) {
        if (dataset[i] == search_key) {
            position = i;
            break;
        }
    }

    // --- CASE 3: A nested sum loop (Generic Complexity Test) ---
    // The model should recognize the O(n^2) structure here.
    long total_sum = 0;
    for (int row = 0; row < total_elements; row++) {
        for (int col = 0; col < total_elements; col++) {
            total_sum += dataset[row];
        }
    }

    printf("Analysis Complete. Position: %d, Sum: %ld\n", position, total_sum);
}

int main() {
    run_analysis();
    return 0;
}