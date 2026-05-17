# GTK4 Example

The Python bindings for libblur work identically in GTK4, with a few differences in how the underlying GDK pointers are retrieved. Since the usage is nearly the same as the GTK3 example, this doesn't include any example widgets — just the binding layer.

## Running

1. Compile the library from the `c/` folder:
    ```bash
    cd ../c && make
    ```
2. Copy `libblur.so` into this folder
3. Run whatever code you have and use the functions the same way as with the GTK3 example.