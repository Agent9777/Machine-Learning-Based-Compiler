#include <stdio.h>
#include <stdlib.h>

// A simulated data processing suite
void run_analysis() {
    int dataset[12] = {10, 50, 30, 70, 80, 60, 20, 90, 40, 100, 11, 22};
    int total_elements = 12;
    int search_key = 60;

    // --- CASE 1: A nested bubble sort with different naming ---
    printf("Sorting dataset...\n");
    ai_optimized_bubble_sort_f3ee(dataset, total_elements);
    }

    // --- CASE 2: A standard linear search ---
    printf("Searching for key...\n");
    int position = -1;
    ai_optimized_linear_search_db2a(dataset, total_elements);

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

// ======= AI OPTIMIZED FUNCTIONS =======

void ai_optimized_bubble_sort_f3ee(int *dataset, int total_elements) {

    // Replaced with qsort
    int _cmp(const void *a, const void *b) { return (*(int*)a - *(int*)b); }
    qsort(dataset, total_elements, sizeof(dataset[0]), _cmp);
}

void ai_optimized_linear_search_db2a(int *dataset, int total_elements) {

    int low = 0, high = total_elements - 1;
    int found_idx = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (dataset[mid] == target) { found_idx = mid; break; }
        if (dataset[mid] < target) low = mid + 1; else high = mid - 1;
    }
    // Logic to handle result can be added here
}