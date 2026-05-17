import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, GtkLayerShell, GLib
import datetime
from blur import enable_blur, disable_blur, free_blur, set_blur_regions_from_widget, is_blur_supported, set_blur_region


class Bar(Gtk.Window):
    def __init__(self, monitor=None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self._blur_ctx = None
        self._blur_enabled = False
        self._use_tracing = False

        # transparent window
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())

        # css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        * {
            all: unset;
        }

        .bar {
            background-color: rgba(20, 20, 20, 0.7);
            border-radius: 14px;
            padding: 6px 12px;
            margin: 8px 12px;
        }

        .bar button {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 2px 10px;
            color: white;
        }

        .bar button:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        .bar label {
            color: white;
        }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # layer shell
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_exclusive_zone(self, 56)
        if monitor:
            GtkLayerShell.set_monitor(self, monitor)

        self.set_size_request(-1, 40)

        # layout
        centerbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        inner.get_style_context().add_class("bar")
        inner.add(centerbox)
        self.add(inner)

        # left
        left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        left.set_hexpand(True)
        left.pack_start(Gtk.Label(label="  Workspace 1"), False, False, 0)
        centerbox.pack_start(left, True, True, 0)

        # center
        self._clock = Gtk.Label(label="")
        centerbox.set_center_widget(self._clock)

        # right
        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        right.set_hexpand(True)

        self._blur_btn = Gtk.Button(label="Blur: OFF")
        self._blur_btn.connect("clicked", self._on_blur_toggle)

        self._trace_btn = Gtk.Button(label="Trace: OFF")
        self._trace_btn.connect("clicked", self._on_trace_toggle)
        self._trace_btn.set_sensitive(False)

        right.pack_end(Gtk.Label(label="100%  "), False, False, 0)
        right.pack_end(self._blur_btn, False, False, 4)
        right.pack_end(self._trace_btn, False, False, 4)
        centerbox.pack_end(right, True, True, 0)

        self._update_clock()
        GLib.timeout_add_seconds(1, self._update_clock)

        self.connect("realize", self._on_realize)
        self.connect("destroy", self._on_destroy)
        self.show_all()

    def _update_clock(self):
        self._clock.set_text(datetime.datetime.now().strftime("%H:%M:%S"))
        return True

    def _on_realize(self, *_):
        if not is_blur_supported(self):
            self._blur_btn.set_sensitive(False)
            self._blur_btn.set_label("Blur: unsupported")
            self._trace_btn.set_sensitive(False)

    def _on_blur_toggle(self, *_):
        if self._blur_enabled:
            self._teardown_blur()
            self._blur_btn.set_label("Blur: OFF")
            self._trace_btn.set_sensitive(False)
            self._trace_btn.set_label("Trace: OFF")
            self._use_tracing = False
        else:
            self._blur_ctx = enable_blur(self)
            self._apply_blur_region()
            self._blur_btn.set_label("Blur: ON")
            self._trace_btn.set_sensitive(True)
        self._blur_enabled = not self._blur_enabled

    def _on_trace_toggle(self, *_):
        self._use_tracing = not self._use_tracing
        self._trace_btn.set_label(f"Trace: {'ON' if self._use_tracing else 'OFF'}")
        if self._blur_ctx:
            self._apply_blur_region()

    def _apply_blur_region(self):
        if not self._blur_ctx:
            return
        if self._use_tracing:
            GLib.idle_add(self._do_trace)
        else:
            alloc = self.get_allocation()
            set_blur_region(self._blur_ctx, 0, 0, alloc.width, alloc.height)

    def _do_trace(self):
        if self._blur_ctx:
            set_blur_regions_from_widget(self._blur_ctx, self, accuracy=1) # Lower is better for accuracy (but worse on cpu)
        return False
    def _teardown_blur(self):
        # Be sure to do this on window visibility toggle too or the program can segfault
        if self._blur_ctx:
            disable_blur(self._blur_ctx)
            free_blur(self._blur_ctx)
            self._blur_ctx = None

    def _on_destroy(self, *_):
        self._teardown_blur()
        Gtk.main_quit()


if __name__ == "__main__":
    bar = Bar()
    Gtk.main()