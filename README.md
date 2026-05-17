# libblur

A small C library (with Python bindings) for applying background blur to GTK windows via the `ext_background_effect_manager_v1` Wayland protocol.

Originally built for use in my GTK shell, but should work fine for any GTK3 or GTK4 project running on a supported compositor.

## Requirements

- A Wayland compositor that supports `ext_background_effect_manager_v1` (e.g. Hyprland)
- GTK3 or GTK4
- Python 3 + `cffi` (for the Python bindings)

## Building

```bash
cd c
make
```

This produces `libblur.so` which the Python bindings expect to find at runtime.
