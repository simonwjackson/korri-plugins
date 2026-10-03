// Send the ICCCM close request directly. Xvfb has no window manager to relay
// xdotool windowquit's EWMH _NET_CLOSE_WINDOW request to the SDL client.
#include <X11/Xlib.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    char *end;
    errno = 0;
    const Window window = strtoul(argv[1], &end, 10);
    if (errno || *end || end == argv[1] || !window) return 2;
    Display *display = XOpenDisplay(NULL);
    if (!display) return 1;
    const Atom close = XInternAtom(display, "WM_DELETE_WINDOW", False);
    Atom *protocols = NULL;
    int count = 0, supported = 0;
    if (XGetWMProtocols(display, window, &protocols, &count)) {
        for (int i = 0; i < count; ++i) supported |= protocols[i] == close;
        XFree(protocols);
    }
    if (!supported) {
        fputs("Native window does not advertise WM_DELETE_WINDOW\n", stderr);
        XCloseDisplay(display);
        return 1;
    }
    XEvent event = {0};
    event.xclient.type = ClientMessage;
    event.xclient.window = window;
    event.xclient.message_type = XInternAtom(display, "WM_PROTOCOLS", False);
    event.xclient.format = 32;
    event.xclient.data.l[0] = close;
    event.xclient.data.l[1] = CurrentTime;
    const int sent = XSendEvent(display, window, False, NoEventMask, &event);
    XSync(display, False);
    XCloseDisplay(display);
    return sent ? 0 : 1;
}
