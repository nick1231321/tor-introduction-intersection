#ifndef HS_WINDOW_SIGNAL_H
#define HS_WINDOW_SIGNAL_H

/* Best-effort in-band signalling to the colocated intersection plugin.
 *
 * The probe client raises "start" immediately before sending INTRODUCE1 and
 * "stop" on receiving RENDEZVOUS2. These two signals delimit the observation
 * window W_i^(j) on the monitored relay's host: the plugin admits destination
 * addresses into the anonymity set only between them (see packet_processer.py).
 *
 * The plugin listens on a unix socket, CONTROL_SOCK (default
 * /run/packet_logger.sock). When no plugin is listening -- for instance when
 * the same binary is used for the introduction-handshake latency measurement
 * against public services -- connect() fails and the signal is silently
 * skipped, so normal operation is never affected. */

#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

static inline void hs_window_signal(const char *cmd) {
    const char *path = getenv("CONTROL_SOCK");
    if (!path) path = "/run/packet_logger.sock";

    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) return;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
        size_t len = strlen(cmd);
        ssize_t w = write(fd, cmd, len);
        (void)w; /* best-effort: ignore short writes */
    }
    close(fd);
}

#endif /* HS_WINDOW_SIGNAL_H */
