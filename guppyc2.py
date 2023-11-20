#!/usr/bin/python3

# Copyright (c) 2023 Dima Krasner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket
import sys
from urllib.parse import urlparse
import select

s = socket.socket(type=socket.SOCK_DGRAM)
url = urlparse(sys.argv[1])
s.connect((url.hostname, 6775))

request = (sys.argv[1] + "\r\n").encode('utf-8')

sys.stderr.write(f"Sending request for {sys.argv[1]}\n")
s.send(request)

buffered = b''
mime_type = None
tries = 0
last_buffered = 0
while True:
	ready, _, _ = select.select([s.fileno()], [], [], 2)

	# if we still haven't received anything from the server, retry the request
	if last_buffered == 0 and not ready:
		if tries > 5:
			raise Exception("All 5 tries have failed")

		sys.stderr.write(f"Retrying request for {sys.argv[1]}\n")
		s.send(request)
		tries += 1
		continue

	# if we're waiting for packet n+1, retry ack packet n
	if not ready and last_buffered > 0:
		sys.stderr.write(f"Retrying ack for packet {last_buffered}\n")
		s.send(f"{last_buffered}\r\n".encode('utf-8'))
		continue

	# receive and parse the next packet
	pkt = s.recv(4096)
	crlf = pkt.index(b'\r\n')
	header = pkt[:crlf]

	try:
		# parse the success packet header
		space = header.index(b' ')
		seq = int(header[:space])
		mime_type = header[space + 1:]

		if seq == 4:
			raise Exception(f"Error: {mime_type.decode('utf-8')}")

		if seq == 3:
			raise Exception(f"Redirected to {mime_type.decode('utf-8')}")

		if seq == 1:
			raise Exception(f"Input required: {mime_type.decode('utf-8')}")

		if seq < 6:
			raise Exception(f"Invalid status code: {seq}")
	except ValueError as e:
		# parse the continuation or EOF packet header
		seq = int(header)

	# ignore this packet if it's not the packet we're waiting for: packet n+1 or the first packet
	if (last_buffered != 0 and seq != last_buffered + 1) or (last_buffered == 0 and mime_type is None):
		sys.stderr.write(f"Ignoring unexpected packet {seq} and sending ack\n")
		s.send(f"{seq}\r\n".encode('utf-8'))
		continue

	if last_buffered == 0 and mime_type is not None:
		sys.stderr.write(f"Response is of type {mime_type.decode('utf-8')}\n")

	sys.stderr.write(f"Sending ack for packet {seq}\n")
	s.send(f"{seq}\r\n".encode('utf-8'))

	data = pkt[crlf + 2:]
	sys.stderr.write(f"Received packet {seq} with {len(data)} bytes of data\n")

	# concatenate the consequentive response chunks we have
	sys.stderr.write(f"Queueing packet {seq} for display\n")
	buffered += data
	last_buffered = seq

	# print the buffered text if we can
	try:
		print(buffered.decode('utf-8'))
		sys.stderr.write("Flushed the buffer to screen\n")
		buffered = b''
	except UnicodeDecodeError:
		sys.stderr.write("Cannot print buffered text until valid UTF-8\n")
		continue

	# stop once we printed everything until the end-of-file packet
	if not data:
		sys.stderr.write("Reached end of document\n")
		break