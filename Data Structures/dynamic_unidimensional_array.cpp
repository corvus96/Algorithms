#include <vector>
#include <iostream>
#include <cstdlib>
#include <type_traits>
#include <new>

using namespace std;

/**
 * @brief Forward declaration of the dynamic array heap structure.
 */
template <typename T> struct D_Array_heap;

/**
 * @brief Initializes a dynamic array heap with given values.
 *
 * @param self   Reference to the heap instance.
 * @param values Pointer to an array of values to copy.
 * @param n      Number of elements to initialize.
 * @return true if initialization succeeds, false otherwise.
 */
template <typename T>
bool init_heap(D_Array_heap<T>&, const T*, size_t);

/**
 * @brief Destroys the heap, calling destructors and freeing memory.
 *
 * @param self Reference to the heap instance.
 */
template <typename T>
void destroy(D_Array_heap<T>&);

/**
 * @brief Prints the contents of the heap to stdout.
 *
 * @param self Reference to the heap instance.
 */
template <typename T>
void print(D_Array_heap<T>& self);

/**
 * @brief Appends a value to the end of the heap.
 *
 * Automatically grows capacity if needed.
 *
 * @param self  Reference to the heap instance.
 * @param value Value to append.
 * @return true if the operation succeeds, false otherwise.
 */
template <typename T>
bool push_back(D_Array_heap<T>& self, const T& value);

/**
 * @brief Removes the last element from the heap.
 *
 * Destroys the element if it has a non-trivial destructor.
 *
 * @param self Reference to the heap instance.
 * @throws std::out_of_range if the heap is empty.
 */
template <typename T>
void pop(D_Array_heap<T>& self);


/**
 * @brief A manually managed dynamic array (heap-based).
 *
 * Mimics a simplified std::vector behavior, supporting:
 *  - initialization
 *  - destruction
 *  - printing
 *  - push_back with automatic resizing
 */
template <typename T>
struct D_Array_heap {
    T* data = nullptr;        ///< Pointer to raw heap storage
    size_t size = 0;          ///< Number of constructed elements
    size_t capacity = 0;      ///< Allocated capacity

    // Function pointers (C-style interface)
    bool (*init_heap)(D_Array_heap<T>&, const T*, size_t) = ::init_heap<T>;
    void (*destroy)(D_Array_heap<T>&) = ::destroy<T>;
    void (*print)(D_Array_heap<T>&) = ::print<T>;
    bool (*push_back)(D_Array_heap<T>&, const T&) = ::push_back<T>;
    void (*pop)(D_Array_heap<T>& self) = ::pop<T>;
};

/**
 * @brief Initializes the heap with a copy of provided values.
 *
 * Uses placement new to properly construct objects.
 * Handles allocation failure and constructor exceptions safely.
 */
template <typename T>
bool init_heap(D_Array_heap<T>& self, const T* values, size_t n) {
    // Invalid input check
    if (n > 0 && values == nullptr) return false;

    // Prevent memory leak if re-initializing
    if (self.data) destroy(self);

    self.size = n;
    self.capacity = n;

    // Allocate raw memory
    self.data = static_cast<T*>(malloc(self.capacity * sizeof(*self.data)));
    if (!self.data) {
        cerr << "Malloc Failed\n";
        self.size = 0;
        self.capacity = 0;
        return false;
    }

    // Construct elements using placement new
    size_t i = 0;
    try {
        for (; i < self.size; ++i) {
            new (self.data + i) T(values[i]);
        }
    } catch (...) {
        // Rollback on construction failure
        for (size_t j = 0; j < i; ++j) self.data[j].~T();
        free(self.data);
        self.data = nullptr;
        self.size = 0;
        self.capacity = 0;
        return false;
    }

    return true;
}

/**
 * @brief Destroys all elements and frees allocated memory.
 */
template <typename T>
void destroy(D_Array_heap<T>& self) {
    for (size_t i = 0; i < self.size; ++i) {
        self.data[i].~T();
    }
    free(self.data);
    self.data = nullptr;
    self.size = 0;
    self.capacity = 0;
}

/**
 * @brief Prints heap contents in array-like format.
 *
 * Example output: [10 20 30]
 */
template <typename T>
void print(D_Array_heap<T>& self) {
    cout << "[";
    for (size_t i = 0; i < self.size; ++i) {
        if (i < self.size - 1) {
            cout << self.data[i] << " ";
        } else {
            cout << self.data[i];
        }
    }
    cout << "]";
}

/**
 * @brief Adds a new element to the end of the heap.
 *
 * Reallocates memory if capacity is exceeded.
 * Optimizes behavior for trivially copyable types.
 */
template <typename T>
bool push_back(D_Array_heap<T>& self, const T& value) {
    // Grow capacity if full
    if (self.size == self.capacity) {
        size_t new_capacity = (self.capacity == 0) ? 1 : self.capacity * 2;

        // Fast path for trivially copyable types
        if constexpr (is_trivially_copyable_v<T>) {
            void* mem = realloc(self.data, new_capacity * sizeof(*self.data));
            if (!mem) {
                cerr << "Realloc Failed\n";
                return false;
            }
            self.data = static_cast<T*>(mem);
            self.capacity = new_capacity;
        } else {
            // Allocate new raw storage
            T* new_data = static_cast<T*>(malloc(new_capacity * sizeof(*self.data)));
            if (!new_data) {
                cerr << "Malloc Failed\n";
                return false;
            }

            // Move-construct old elements
            size_t i = 0;
            try {
                for (; i < self.size; ++i) {
                    new (new_data + i) T(move(self.data[i]));
                }
                // Construct new element
                new (new_data + self.size) T(value);
            } catch (...) {
                for (size_t j = 0; j < i; ++j) new_data[j].~T();
                free(new_data);
                return false;
            }

            // Destroy old storage
            for (size_t k = 0; k < self.size; ++k) self.data[k].~T();
            free(self.data);

            self.data = new_data;
            self.capacity = new_capacity;
            ++self.size;
            return true;
        }
    }

    // Enough capacity: just construct element
    if constexpr (is_trivially_copyable_v<T>) {
        self.data[self.size] = value;
    } else {
        new (self.data + self.size) T(value);
    }

    ++self.size;
    return true;
}

/**
 * @brief Removes the last element from the heap.
 *
 * Ends the lifetime of the element and reduces the logical size.
 */
template <typename T>
void pop(D_Array_heap<T>& self){
    if(self.size == 0){
        throw out_of_range("pop on empty array");
    }
    if constexpr (is_trivially_destructible_v<T>){
        self.data[self.size - 1].~T();
    }
    --self.size;
}

int main() {
    D_Array_heap<int> arr;
    D_Array_heap<string> arr2;

    int values[] = {10, 20, 30, 40};
    string values2[] = {"true", "false", "false", "true"};

    arr.init_heap(arr, values, 4);
    arr2.init_heap(arr2, values2, 4);

    arr.print(arr);
    arr2.print(arr2);

    arr.push_back(arr, 5);
    arr2.push_back(arr2, "hola");

    arr.print(arr);
    arr2.print(arr2);
    arr.pop(arr);
    arr2.pop(arr2);
    arr.print(arr);
    arr2.print(arr2);

    arr.destroy(arr);
    arr2.destroy(arr2);
}
