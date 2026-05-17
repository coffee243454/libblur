# GTK3 Example

A minimal bar demonstrating libblur with GTK3.

Includes a basic layer shell bar with a toggle for blur and widget region tracing, so you can see how the blur region follows the widget's visible shape (including rounded corners).

## Running

1. Compile the library from the `c/` folder:
    ```bash
    cd ../c && make
    ```
2. Copy `libblur.so` into this folder
3. Run:
    ```bash
    python3 main.py
    ```

## Screenshots
### No Blur
![Bar with no blur (no tracing)](screenshots/no_blur.png)
### Blur with no tracing
![Bar with blur (no tracing)](screenshots/blur_no_tracing.png)
### Blur and tracing
![Bar with blur (tracing enabled)](screenshots/blur_and_tracing.png)
