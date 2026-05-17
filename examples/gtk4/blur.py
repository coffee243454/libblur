from cffi import FFI
ffi = FFI()

ffi.cdef("""
    typedef struct BlurContext BlurContext;

    int          blur_supported(void *wl_display);
    BlurContext* blur_enable(void *wl_display, void *wl_surface);
    void         blur_set_region(BlurContext *ctx,
                                 int32_t x, int32_t y,
                                 int32_t width, int32_t height);
    void         blur_set_regions(BlurContext *ctx,
                                  const int32_t *xs, const int32_t *ys,
                                  const int32_t *widths, const int32_t *heights,
                                  int count);
    void         blur_disable(BlurContext *ctx);
    void         blur_free(BlurContext *ctx);

    typedef struct _GtkWidget  GtkWidget;
    typedef struct _GtkNative  GtkNative;
    typedef struct _GdkSurface GdkSurface;
    typedef struct _GdkDisplay GdkDisplay;

    GtkNative*  gtk_widget_get_native(GtkWidget *widget);
    GdkSurface* gtk_native_get_surface(GtkNative *native);
    GdkDisplay* gtk_widget_get_display(GtkWidget *widget);

    void* gdk_wayland_display_get_wl_display(GdkDisplay *display);
    void* gdk_wayland_surface_get_wl_surface(GdkSurface *surface);
""")

libgtk = ffi.dlopen("libgtk-4.so.1")
libblur = ffi.dlopen("./libblur.so")


def _get_wl_pointers(widget):
    ptr     = ffi.cast("GtkWidget*", hash(widget))
    native  = libgtk.gtk_widget_get_native(ptr)
    gdk_win = libgtk.gtk_native_get_surface(native)
    gdk_dpy = libgtk.gtk_widget_get_display(ptr)

    if not gdk_win:
        raise RuntimeError(
            "Widget has no GDK surface — is it realized? "
            "Connect to the 'realize' signal before calling blur functions."
        )

    wl_display = libgtk.gdk_wayland_display_get_wl_display(gdk_dpy)
    wl_surface = libgtk.gdk_wayland_surface_get_wl_surface(gdk_win)

    return wl_display, wl_surface

def is_blur_supported(widget) -> bool:
    wl_display, _ = _get_wl_pointers(widget)
    return bool(libblur.blur_supported(wl_display))


def enable_blur(widget) -> "BlurContext":
    wl_display, wl_surface = _get_wl_pointers(widget)
    ctx = libblur.blur_enable(wl_display, wl_surface)

    if not ctx:
        raise RuntimeError(
            "blur_enable failed — compositor may not support "
            "ext_background_effect_manager_v1"
        )

    return ctx


def set_blur_region(ctx, x: int, y: int, width: int, height: int):
    libblur.blur_set_region(ctx, x, y, width, height)


def set_blur_regions(ctx, rects: list[tuple[int, int, int, int]]):
    count = len(rects)
    if count == 0:
        return

    xs      = ffi.new("int32_t[]", [r[0] for r in rects])
    ys      = ffi.new("int32_t[]", [r[1] for r in rects])
    widths  = ffi.new("int32_t[]", [r[2] for r in rects])
    heights = ffi.new("int32_t[]", [r[3] for r in rects])

    libblur.blur_set_regions(ctx, xs, ys, widths, heights, count)


# def set_blur_regions_from_widget(ctx, widget, accuracy: int = 10,
#                                  alpha_threshold: int = 10):
#     rects = trace_widget_regions(widget, accuracy=accuracy, alpha_threshold=alpha_threshold)
#     set_blur_regions(ctx, [(r.x, r.y, r.width, r.height) for r in rects])


def disable_blur(ctx):
    libblur.blur_disable(ctx)


def free_blur(ctx):
    libblur.blur_free(ctx)
