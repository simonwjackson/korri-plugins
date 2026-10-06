// Test-only interposer: pause after SDL creates the first real visible window,
// before OTRGlobals::Initialize replaces signal handlers or starts audio.
#define _GNU_SOURCE
#include <dlfcn.h>
#include <signal.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

typedef struct SDL_Window SDL_Window;
typedef SDL_Window *(*CreateWindow)(const char *, int, int, int, int, uint32_t);

SDL_Window *SDL_CreateWindow(const char *title, int x, int y, int width,
                             int height, uint32_t flags) {
    CreateWindow create = (CreateWindow)dlsym(RTLD_NEXT, "SDL_CreateWindow");
    if (!create) _exit(125);
    SDL_Window *window = create(title, x, y, width, height, flags);
    if (window && getenv("KORRI_2SHIP_PAUSE_FIRST_WINDOW")) {
        unsetenv("KORRI_2SHIP_PAUSE_FIRST_WINDOW");
        static const char marker[] = "2 Ship early-window test paused before Initialize\n";
        if (write(STDERR_FILENO, marker, sizeof(marker) - 1) < 0) _exit(125);
        raise(SIGSTOP);
    }
    return window;
}
