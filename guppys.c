/*
 * Copyright (c) 2023 Dima Krasner
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <string.h>
#include <limits.h>
#include <fcntl.h>
#include <time.h>
#include <stdio.h>
#include <poll.h>
#include <errno.h>
#include <stdio.h>
#include <arpa/inet.h>

#define PORT "6775"
#define MAX_SESSIONS 32
#define MAX_CHUNKS 8
#define CHUNK_SIZE 512

int main(int argc, char *argv[])
{
	static struct {
		struct {
			struct sockaddr_storage peer;
			char addrstr[INET6_ADDRSTRLEN];
			unsigned short port;
			struct timespec started;
			int fd, first, next, last;
			struct {
				char data[CHUNK_SIZE];
				struct timespec sent;
				ssize_t len;
				int seq;
			} chunks[MAX_CHUNKS];
		} sessions[MAX_SESSIONS];
	} server;
	static char buf[2049];
	char *end;
	struct pollfd pfd;
	const char *path, *errstr;
	const void *saddr;
	struct addrinfo hints = {
		.ai_family = AF_INET6,
		.ai_flags = AI_PASSIVE | AI_V4MAPPED,
		.ai_socktype = SOCK_DGRAM
	}, *addr;
	struct sockaddr_storage peer;
	struct timespec now;
	const struct sockaddr_in *peerv4 = (const struct sockaddr_in *)&peer;
	const struct sockaddr_in6 *peerv6 = (const struct sockaddr_in6 *)&peer;
	long seq;
	ssize_t len;
	int s, sndbuf = MAX_SESSIONS * MAX_CHUNKS * CHUNK_SIZE, one = 1, off, ret;
	unsigned int slot, active = 0, i, j, ready, waiting;
	socklen_t peerlen;
	unsigned short sport;

	// start listening for packets and increase the buffer size for sending
	if (getaddrinfo(NULL, PORT, &hints, &addr) != 0) return EXIT_FAILURE;
	if (
		(s = socket(addr->ai_family,addr->ai_socktype, addr->ai_protocol)) < 0
	) {
		freeaddrinfo(addr);
		return EXIT_FAILURE;
	}
	if (
		setsockopt(s, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf)) < 0 ||
		setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) < 0 ||
		bind(s, addr->ai_addr, addr->ai_addrlen) < 0
	) {
		close(s);
		freeaddrinfo(addr);
		return EXIT_FAILURE;
	}
	freeaddrinfo(addr);

	// restrict access to files outside the working directory
	if (chroot(".") < 0) {
		close(s);
		return EXIT_FAILURE;
	}

	pfd.events = POLLIN;
	pfd.fd = s;

	srand((unsigned int)time(NULL));

	for (i = 0; i < MAX_SESSIONS; ++i) {
		server.sessions[i].fd = -1;
		server.sessions[i].peer.ss_family = AF_UNSPEC;
	}

	while (1) {
		// wait for an incoming packet with timeout of 100ms if we have active sessions
		pfd.revents = 0;
		ready = poll(&pfd, 1, active ? 100 : -1);
		if (ready < 0) break;

		if (ready == 0 || !(pfd.revents & POLLIN)) goto respond;

		// receive a packet
		peerlen = sizeof(peer);
		if (
			(len = recvfrom(
				s,
				buf,
				sizeof(buf) - 1,
				0,
				(struct sockaddr *)&peer,
				&peerlen
			)) <= 0
		) break;

		// the smallest valid packet we can receive is 6\r\n
		if (len < 3 || buf[len - 2] != '\r' || buf[len - 1] != '\n') continue;

		// check if this packet belongs to an existing session by comparing the
		// source address of the packet
		switch (peer.ss_family) {
		case AF_INET:
			sport = ntohs(peerv4->sin_port);
			saddr = &peerv4->sin_addr;
			break;
		case AF_INET6:
			sport = ntohs(peerv6->sin6_port);
			saddr = &peerv6->sin6_addr;
			break;
		default:
			continue;
		}

		slot = MAX_SESSIONS;

		for (i = sport % MAX_SESSIONS; i < MAX_SESSIONS; ++i) {
			if (
				memcmp(
					&peer,
					&server.sessions[i].peer,
					sizeof(struct sockaddr_storage)
				) == 0
			) {
				slot = i;
				goto have_slot;
			}
		}

		for (i = 0; i < sport % MAX_SESSIONS; ++i) {
			if (
				memcmp(
					&peer,
					&server.sessions[i].peer,
					sizeof(struct sockaddr_storage)
				) == 0) {
				slot = i;
				break;
			}
		}

have_slot:
		// if all slots are occupied, send an error packet
		if (slot == MAX_SESSIONS && active == MAX_SESSIONS) {
			fputs("Too many sessions", stderr);
			sendto(
				s,
				"4 Too many sessions\r\n",
				21,
				0,
				(const struct sockaddr *)&peer,
				peerlen
			);
			continue;
		}

		// if no session matches this packet ...
		if (slot == MAX_SESSIONS) {
			// parse and validate the request
			if (len < 11 || memcmp(buf, "guppy://", 8)) continue;
			buf[len - 2] = '\0';
			if (
				!(path = strchr(&buf[8], '/')) ||
				!path[0] ||
				(path[0] == '/' && !path[1])
			) path = "index.gmi";
			else ++path;

			// find an empty slot
			for (i = 0; i < MAX_SESSIONS; ++i) {
				if (server.sessions[i].fd < 0) {
					slot = i;
					break;
				}
			}

			if (
				!inet_ntop(
					peer.ss_family,
					saddr,
					server.sessions[slot].addrstr,
					sizeof(server.sessions[slot].addrstr)
				)
			) continue;

			if ((server.sessions[slot].fd = open(path, O_RDONLY)) < 0) {
				errstr = strerror(errno);
				fprintf(
					stderr,
					"Failed to open %s for %s:%hu: %s\n",
					path,
					server.sessions[slot].addrstr,
					server.sessions[slot].port,
					errstr
				);
				ret = snprintf(buf, sizeof(buf), "4 %s\r\n", errstr);
				if (ret > 0 && ret < sizeof(buf))
					sendto(
						s,
						buf,
						(size_t)ret,
						0,
						(const struct sockaddr *)&peer,
						peerlen
					);
				continue;
			}

			memcpy(
				&server.sessions[slot].peer,
				&peer,
				sizeof(struct sockaddr_storage)
			);
			server.sessions[slot].port = sport;
			server.sessions[slot].first = 6 + (rand() % SHRT_MAX);
			server.sessions[slot].next = server.sessions[slot].first;
			server.sessions[slot].last = 0;
			server.sessions[slot].started = now;
			for (i = 0; i < MAX_CHUNKS; ++i)
				server.sessions[slot].chunks[i].seq = 0;
			++active;
		} else {
			// extract the sequence number from the acknowledgement packet
			buf[len] = '\0';
			if (
				(seq = strtol(buf, &end, 10)) < server.sessions[slot].first ||
				(seq >= server.sessions[slot].next) ||
				!end ||
				len != (end - buf) + 2
			)
				goto respond;

			// acknowledge the packet
			for (i = 0; i < MAX_CHUNKS; ++i) {
				if (server.sessions[slot].chunks[i].seq == seq) {
					fprintf(
						stderr,
						"%s:%hu has received %ld\n",
						server.sessions[slot].addrstr,
						server.sessions[slot].port,
						seq
					);
					server.sessions[slot].chunks[i].seq = 0;
				} else if (server.sessions[slot].chunks[i].seq) ++waiting;
			}
		}

		// fill all free slots with more chunks that can be sent
		for (i = 0; i < MAX_CHUNKS && !server.sessions[slot].last; ++i) {
			if (server.sessions[slot].chunks[i].seq) continue;

			server.sessions[slot].chunks[i].seq = server.sessions[slot].next;

			if (
				server.sessions[slot].chunks[i].seq ==
													server.sessions[slot].first
			)
				off = sprintf(
					server.sessions[slot].chunks[i].data,
					"%d text/gemini\r\n",
					server.sessions[slot].chunks[i].seq
				);
			else
				off = sprintf(
					server.sessions[slot].chunks[i].data,
					"%d\r\n",
					server.sessions[slot].chunks[i].seq
				);

			server.sessions[slot].chunks[i].len = read(
				server.sessions[slot].fd,
				&server.sessions[slot].chunks[i].data[off],
				sizeof(server.sessions[slot].chunks[i].data) - off
			);
			if (server.sessions[slot].chunks[i].len < 0) {
				fprintf(
					stderr,
					"Failed to read file for %s:%hu: %s\n",
					server.sessions[slot].addrstr,
					server.sessions[slot].port,
					strerror(errno)
				);
				server.sessions[slot].chunks[i].len = off;
			} else if (server.sessions[slot].chunks[i].len == 0)
				server.sessions[slot].chunks[i].len = off;
			else server.sessions[slot].chunks[i].len += off;

			if (
				server.sessions[slot].chunks[i].len == off &&
				!server.sessions[slot].last
			) server.sessions[slot].last = server.sessions[slot].chunks[i].seq;
			server.sessions[slot].chunks[i].sent.tv_sec = 0;

			++server.sessions[slot].next;
		}

respond:
		if (clock_gettime(CLOCK_MONOTONIC, &now) < 0) break;

		for (i = 0; i < MAX_SESSIONS; ++i) {
			if (server.sessions[i].fd < 0) continue;

			// terminate sessions after 20s
			if (now.tv_sec > server.sessions[i].started.tv_sec + 20) {
				fprintf(
					stderr,
					"%s:%hu has timed out\n",
					server.sessions[i].addrstr,
					server.sessions[i].port
				);
				close(server.sessions[i].fd);
				server.sessions[i].fd = -1;
				--active;
				continue;
			}

			// send unacknowledged chunks if not sent or every 2s
			waiting = 0;
			for (j = 0; j < MAX_CHUNKS; ++j) {
				if (server.sessions[i].chunks[j].seq == 0) continue;

				++waiting;

				if (server.sessions[i].chunks[j].sent.tv_sec == 0) fprintf(
					stderr, "Sending %d to %s:%hu\n",
					server.sessions[i].chunks[j].seq,
					server.sessions[i].addrstr,
					server.sessions[i].port
				);
				else if (
					now.tv_sec < server.sessions[i].chunks[j].sent.tv_sec + 2
				) continue;
				else fprintf(
					stderr,
					"Resending %d to %s:%hu\n",
					server.sessions[i].chunks[j].seq,
					server.sessions[i].addrstr,
					server.sessions[i].port
				);

				if (
					sendto(
						s,
						server.sessions[i].chunks[j].data,
						server.sessions[i].chunks[j].len,
						0,
						(const struct sockaddr *)&server.sessions[i].peer,
						sizeof(server.sessions[i].peer)
					) < 0
				) fprintf(
					stderr,
					"Failed to send packet to %s:%hu: %s\n",
					server.sessions[i].addrstr,
					server.sessions[i].port,
					strerror(errno)
				);
				else server.sessions[i].chunks[j].sent = now;
			}

			// if all packets are acknowledged, terminate the session
			if (waiting == 1)
				fprintf(
					stderr,
					"%s:%hu has 1 pending packet\n",
					server.sessions[i].addrstr,
					server.sessions[i].port
				);
			else if (waiting > 1)
				fprintf(
					stderr,
					"%s:%hu has %d pending packets\n",
					server.sessions[i].addrstr,
					server.sessions[i].port,
					waiting
				);
			else {
				fprintf(
					stderr,
					"%s:%hu has received all packets\n",
					server.sessions[i].addrstr,
					server.sessions[i].port
				);
				close(server.sessions[i].fd);
				server.sessions[i].fd = -1;
				--active;
			}
		}
	}

	for (i = 0; i < MAX_SESSIONS; ++i) {
		if (server.sessions[i].fd >= 0) close(server.sessions[i].fd);
	}
	close(s);
	return EXIT_SUCCESS;
}
