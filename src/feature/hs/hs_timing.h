#ifndef HS_TIMING_H
#define HS_TIMING_H

/* small POSIX/C headers required by the CSV-timing helpers */
#include <sys/time.h>
#include <time.h>
#include <stdint.h>
#include <inttypes.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>

/* epoch ms */
static inline uint64_t now_ms_epoch(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000 + (uint64_t)tv.tv_usec / 1000;
}

/* bytes -> hex (dest must be 2*len+1) */
static inline void bytes_to_hex(const void *buf, size_t len, char *dest) {
    static const char hex[] = "0123456789abcdef";
    const unsigned char *b = (const unsigned char*)buf;
    for (size_t i = 0; i < len; ++i) {
        dest[2*i    ] = hex[(b[i] >> 4) & 0xF];
        dest[2*i + 1] = hex[b[i] & 0xF];
    }
    dest[2*len] = '\0';
}

/* Append one CSV line (single write). No tor_log(); minimal stderr diagnostics. */
static inline void hs_timing_csv_append(const char *tag, const void *rend_circ,
                                        const void *cookie_buf, size_t cookie_len)
{
    const char *path = getenv("TOR_HS_TIMING_CSV");
    if (!path) path = "/tmp/tor_hs_timing.csv";

    uint64_t ms = now_ms_epoch();
    time_t sec = (time_t)(ms / 1000);
    int msec = (int)(ms % 1000);

    struct tm tm_buf;
    char iso[64];
    if (gmtime_r(&sec, &tm_buf) == NULL) {
        strncpy(iso, "1970-01-01T00:00:00", sizeof(iso));
        iso[sizeof(iso)-1] = '\0';
    } else {
        strftime(iso, sizeof(iso), "%Y-%m-%dT%H:%M:%S", &tm_buf);
    }
    char iso_ms[80];
    snprintf(iso_ms, sizeof(iso_ms), "%s.%03dZ", iso, msec);

    char cookie_hex[2 * (cookie_len ? cookie_len : 1) + 1];
    if (cookie_buf && cookie_len > 0) {
        bytes_to_hex(cookie_buf, cookie_len, cookie_hex);
    } else {
        cookie_hex[0] = '\0';
    }

    char line[512];
    int n = snprintf(line, sizeof(line), "%s,%" PRIu64 ",%s,%p,%s\n",
                     iso_ms, ms, tag, rend_circ, cookie_hex);
    if (n <= 0) return;

    int fd = open(path, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) {
        /* silent or write to stderr for debug; comment out if you want fully silent */
        fprintf(stderr, "HS-TIMING: open(%s) failed: %s\n", path, strerror(errno));
        return;
    }

    ssize_t w = write(fd, line, (size_t)n);
    if (w != n) {
        fprintf(stderr, "HS-TIMING: partial/failed write to %s: %s\n", path, strerror(errno));
    }

    if (getenv("TOR_HS_TIMING_FSYNC")) {
        if (fsync(fd) < 0) {
            fprintf(stderr, "HS-TIMING: fsync(%s) failed: %s\n", path, strerror(errno));
        }
    }
    close(fd);
}

#endif /* HS_TIMING_H */

