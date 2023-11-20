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
from urllib.parse import urlparse, unquote
import select
import random
import io
import time
import sys
import logging
import collections

home = """# Home

=> /lorem Lorem ipsum
=> /echo Echo
=> /rick.mp4 Rick Astley - Never Gonna Give You Up
"""

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Pharetra diam sit amet nisl suscipit adipiscing bibendum est ultricies. Et tortor at risus viverra adipiscing at in tellus integer. Est ante in nibh mauris cursus mattis molestie. At varius vel pharetra vel turpis nunc. Consectetur adipiscing elit pellentesque habitant morbi tristique. Eu scelerisque felis imperdiet proin fermentum leo vel. At tempor commodo ullamcorper a. At augue eget arcu dictum varius duis at consectetur. Condimentum mattis pellentesque id nibh tortor id. Lorem ipsum dolor sit amet. Enim sed faucibus turpis in eu. Aenean sed adipiscing diam donec adipiscing tristique risus nec. Rutrum quisque non tellus orci ac auctor augue mauris augue. Posuere lorem ipsum dolor sit. Egestas erat imperdiet sed euismod nisi porta lorem mollis aliquam.

Mi proin sed libero enim sed. Risus nec feugiat in fermentum posuere urna nec. Leo vel orci porta non pulvinar neque laoreet. Nisl purus in mollis nunc. Ipsum consequat nisl vel pretium. Sit amet tellus cras adipiscing enim eu turpis egestas. Nunc mattis enim ut tellus elementum sagittis vitae. Quis enim lobortis scelerisque fermentum dui faucibus. Fringilla est ullamcorper eget nulla. Viverra nibh cras pulvinar mattis nunc sed blandit. Placerat orci nulla pellentesque dignissim. Habitant morbi tristique senectus et netus et malesuada. Id eu nisl nunc mi ipsum faucibus vitae aliquet.

Ultricies mi eget mauris pharetra et ultrices neque. Felis donec et odio pellentesque. Mauris vitae ultricies leo integer. A pellentesque sit amet porttitor eget dolor morbi. Et ligula ullamcorper malesuada proin libero nunc consequat. Donec massa sapien faucibus et molestie. Elementum tempus egestas sed sed. Ut sem viverra aliquet eget sit. Aliquam eleifend mi in nulla posuere sollicitudin. Et leo duis ut diam quam. Duis at consectetur lorem donec massa sapien faucibus et molestie. Sit amet venenatis urna cursus eget nunc scelerisque viverra mauris. Risus commodo viverra maecenas accumsan lacus. Vestibulum lectus mauris ultrices eros in cursus turpis massa. Purus sit amet volutpat consequat mauris nunc congue nisi. Enim nunc faucibus a pellentesque sit amet porttitor eget dolor. Auctor urna nunc id cursus metus aliquam eleifend.

Ante in nibh mauris cursus mattis molestie a iaculis at. Quam pellentesque nec nam aliquam sem. Massa tincidunt nunc pulvinar sapien et ligula ullamcorper. Non blandit massa enim nec dui nunc mattis. Est ante in nibh mauris cursus. A diam maecenas sed enim ut sem viverra aliquet. Ornare aenean euismod elementum nisi quis. Est pellentesque elit ullamcorper dignissim cras tincidunt lobortis feugiat. Euismod in pellentesque massa placerat duis ultricies lacus. Volutpat maecenas volutpat blandit aliquam etiam erat. Tincidunt ornare massa eget egestas. Tellus molestie nunc non blandit massa enim nec dui nunc. At quis risus sed vulputate odio. Urna molestie at elementum eu. Enim lobortis scelerisque fermentum dui faucibus in ornare quam viverra. Leo vel fringilla est ullamcorper. Morbi tristique senectus et netus et malesuada fames. Faucibus ornare suspendisse sed nisi lacus sed viverra.

Tellus in hac habitasse platea dictumst vestibulum rhoncus. Praesent elementum facilisis leo vel fringilla est. Lorem ipsum dolor sit amet consectetur. Donec ultrices tincidunt arcu non sodales neque sodales. Dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim. At quis risus sed vulputate. Tincidunt nunc pulvinar sapien et ligula ullamcorper malesuada proin. Orci sagittis eu volutpat odio facilisis. Ut tellus elementum sagittis vitae et leo duis ut diam. Donec et odio pellentesque diam volutpat commodo sed egestas egestas. Facilisis volutpat est velit egestas dui id ornare arcu odio. Rutrum quisque non tellus orci ac auctor augue mauris augue. Tortor condimentum lacinia quis vel eros donec ac. Ac tortor dignissim convallis aenean. Felis imperdiet proin fermentum leo vel orci porta. Purus in mollis nunc sed id. Eget aliquet nibh praesent tristique magna sit amet. Consequat nisl vel pretium lectus quam id leo.

Aliquam purus sit amet luctus venenatis lectus magna. Ac tortor vitae purus faucibus ornare. Convallis posuere morbi leo urna. Nulla posuere sollicitudin aliquam ultrices sagittis orci a. Adipiscing elit ut aliquam purus sit amet luctus. Sit amet mattis vulputate enim. Pellentesque habitant morbi tristique senectus. Faucibus nisl tincidunt eget nullam non nisi. Purus gravida quis blandit turpis cursus in. Aliquam nulla facilisi cras fermentum odio eu feugiat pretium nibh. Pharetra et ultrices neque ornare aenean euismod.

Suspendisse sed nisi lacus sed. Cursus sit amet dictum sit amet justo donec. Eget nunc lobortis mattis aliquam. Eget nullam non nisi est sit amet. Turpis cursus in hac habitasse platea dictumst quisque. Aliquam id diam maecenas ultricies mi. Vitae congue eu consequat ac felis. Facilisi nullam vehicula ipsum a arcu cursus vitae congue. Vitae nunc sed velit dignissim sodales. Placerat orci nulla pellentesque dignissim enim sit amet venenatis. Nibh tellus molestie nunc non. Id diam vel quam elementum pulvinar etiam non quam.

Mus mauris vitae ultricies leo integer malesuada nunc. Varius quam quisque id diam vel quam. Lorem ipsum dolor sit amet consectetur. Congue quisque egestas diam in arcu cursus euismod quis. Id nibh tortor id aliquet lectus proin nibh nisl condimentum. Facilisis magna etiam tempor orci eu lobortis elementum nibh. Sit amet porttitor eget dolor morbi non. Et odio pellentesque diam volutpat commodo. Urna molestie at elementum eu facilisis. Enim neque volutpat ac tincidunt vitae. Proin libero nunc consequat interdum varius. Enim diam vulputate ut pharetra sit amet aliquam id. Eu augue ut lectus arcu bibendum at varius vel. Leo vel orci porta non pulvinar neque laoreet suspendisse. Orci eu lobortis elementum nibh tellus molestie nunc non blandit.

Congue quisque egestas diam in arcu cursus. Tellus molestie nunc non blandit massa. Turpis massa tincidunt dui ut. Diam quis enim lobortis scelerisque fermentum dui. Sed id semper risus in hendrerit gravida rutrum quisque non. Amet porttitor eget dolor morbi non arcu risus quis. Dolor sit amet consectetur adipiscing elit pellentesque. Id donec ultrices tincidunt arcu. Ut placerat orci nulla pellentesque dignissim. Et netus et malesuada fames ac turpis egestas maecenas. Feugiat vivamus at augue eget.

Sit amet commodo nulla facilisi nullam vehicula. Nunc consequat interdum varius sit amet mattis vulputate. Nisl rhoncus mattis rhoncus urna. Dui accumsan sit amet nulla facilisi morbi. Donec ac odio tempor orci dapibus ultrices in iaculis nunc. Tellus integer feugiat scelerisque varius morbi enim nunc faucibus a. Lobortis mattis aliquam faucibus purus in massa tempor. In cursus turpis massa tincidunt dui ut ornare lectus sit. Vitae et leo duis ut diam quam nulla porttitor. Sollicitudin aliquam ultrices sagittis orci a scelerisque purus semper. Vestibulum sed arcu non odio euismod lacinia at quis risus. A diam sollicitudin tempor id eu. Vulputate sapien nec sagittis aliquam malesuada bibendum arcu vitae elementum.

Egestas fringilla phasellus faucibus scelerisque. Arcu non sodales neque sodales. Diam vulputate ut pharetra sit amet aliquam id diam. Eget mauris pharetra et ultrices neque ornare aenean. Vestibulum sed arcu non odio euismod. Nam aliquam sem et tortor consequat id porta. Leo integer malesuada nunc vel risus commodo viverra. Et leo duis ut diam quam nulla porttitor massa id. Lorem dolor sed viverra ipsum nunc aliquet bibendum. Sapien eget mi proin sed libero enim. Fermentum odio eu feugiat pretium. Scelerisque eu ultrices vitae auctor. Cursus euismod quis viverra nibh cras pulvinar mattis. Pulvinar neque laoreet suspendisse interdum consectetur libero id. A condimentum vitae sapien pellentesque habitant morbi tristique senectus.

Massa vitae tortor condimentum lacinia quis vel eros donec ac. Cursus metus aliquam eleifend mi in nulla posuere sollicitudin aliquam. Quis auctor elit sed vulputate mi sit amet. Diam maecenas ultricies mi eget. Eget dolor morbi non arcu. Cras sed felis eget velit. Amet luctus venenatis lectus magna fringilla urna. Nec feugiat in fermentum posuere urna nec tincidunt praesent semper. Tincidunt ornare massa eget egestas. Vel eros donec ac odio tempor orci dapibus ultrices. Egestas sed tempus urna et pharetra pharetra massa massa ultricies. Aliquam nulla facilisi cras fermentum odio eu. Consequat mauris nunc congue nisi vitae suscipit tellus mauris. Nam at lectus urna duis convallis convallis tellus id. Et netus et malesuada fames ac turpis egestas. Faucibus purus in massa tempor nec feugiat nisl. Ultricies leo integer malesuada nunc vel. Ultricies mi eget mauris pharetra et ultrices neque ornare aenean. Tristique risus nec feugiat in fermentum posuere urna. Aenean pharetra magna ac placerat vestibulum lectus mauris ultrices.

Eleifend donec pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Consequat nisl vel pretium lectus quam id leo. Ultrices eros in cursus turpis. Faucibus in ornare quam viverra orci sagittis. Dictum varius duis at consectetur. Quis auctor elit sed vulputate. Placerat duis ultricies lacus sed. Ut etiam sit amet nisl purus in. Varius vel pharetra vel turpis nunc eget lorem dolor sed. Turpis in eu mi bibendum neque egestas. Id neque aliquam vestibulum morbi blandit. Mauris commodo quis imperdiet massa tincidunt nunc. Amet commodo nulla facilisi nullam vehicula ipsum. Tortor posuere ac ut consequat semper viverra nam libero justo. Commodo nulla facilisi nullam vehicula ipsum a arcu.

Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget egestas. Ornare lectus sit amet est placerat in egestas erat imperdiet. In arcu cursus euismod quis viverra nibh cras pulvinar mattis. Luctus accumsan tortor posuere ac ut consequat semper viverra nam. Dolor magna eget est lorem ipsum. Lobortis feugiat vivamus at augue eget arcu dictum. Vestibulum mattis ullamcorper velit sed. Id nibh tortor id aliquet lectus. Ultricies lacus sed turpis tincidunt. Iaculis urna id volutpat lacus laoreet non. Tellus pellentesque eu tincidunt tortor aliquam. Enim nec dui nunc mattis enim ut. Quis varius quam quisque id diam. Purus ut faucibus pulvinar elementum integer. Placerat duis ultricies lacus sed turpis tincidunt id aliquet risus. Neque sodales ut etiam sit amet nisl purus. Nec feugiat nisl pretium fusce id velit.

Ultrices eros in cursus turpis massa tincidunt dui ut. In massa tempor nec feugiat nisl pretium fusce. Sed id semper risus in hendrerit gravida rutrum quisque. Condimentum lacinia quis vel eros donec ac odio tempor. Nunc sed blandit libero volutpat sed cras. Et leo duis ut diam quam. Ullamcorper sit amet risus nullam. Semper auctor neque vitae tempus quam pellentesque nec nam aliquam. Urna id volutpat lacus laoreet non curabitur. Sem et tortor consequat id porta nibh. Rhoncus mattis rhoncus urna neque viverra justo nec ultrices. Tristique nulla aliquet enim tortor at auctor urna nunc. Scelerisque felis imperdiet proin fermentum leo vel orci porta. Massa ultricies mi quis hendrerit dolor magna. Suscipit tellus mauris a diam maecenas sed enim. Duis ut diam quam nulla porttitor massa. Tempus quam pellentesque nec nam aliquam sem. Vulputate sapien nec sagittis aliquam malesuada bibendum arcu. Amet purus gravida quis blandit. Risus commodo viverra maecenas accumsan lacus vel facilisis volutpat est.

Aliquam id diam maecenas ultricies mi eget. Tincidunt dui ut ornare lectus. Arcu ac tortor dignissim convallis aenean et tortor at risus. Cursus risus at ultrices mi tempus imperdiet nulla. Eu consequat ac felis donec et odio. Curabitur gravida arcu ac tortor dignissim. Scelerisque viverra mauris in aliquam sem. Nullam non nisi est sit amet facilisis magna etiam tempor. Velit euismod in pellentesque massa placerat duis ultricies. Urna id volutpat lacus laoreet non curabitur. Praesent elementum facilisis leo vel fringilla est ullamcorper. Lorem sed risus ultricies tristique nulla aliquet enim tortor. Erat velit scelerisque in dictum non consectetur. Imperdiet dui accumsan sit amet nulla facilisi. Sapien et ligula ullamcorper malesuada proin. Amet commodo nulla facilisi nullam vehicula ipsum a arcu. Mi in nulla posuere sollicitudin aliquam ultrices sagittis orci. Urna condimentum mattis pellentesque id nibh tortor id aliquet. Amet venenatis urna cursus eget nunc. Elementum sagittis vitae et leo duis.

Feugiat in fermentum posuere urna nec tincidunt. Sem nulla pharetra diam sit amet nisl suscipit adipiscing. Sed blandit libero volutpat sed cras. Arcu dictum varius duis at. Porttitor massa id neque aliquam vestibulum morbi blandit. Dui faucibus in ornare quam viverra orci sagittis. Nisi quis eleifend quam adipiscing vitae proin sagittis nisl. Duis ut diam quam nulla porttitor massa id neque. Convallis a cras semper auctor. Mauris a diam maecenas sed enim ut. Urna id volutpat lacus laoreet non curabitur gravida arcu ac.

Pellentesque eu tincidunt tortor aliquam nulla. Semper risus in hendrerit gravida rutrum quisque non tellus orci. Sed vulputate mi sit amet mauris commodo quis imperdiet massa. Posuere morbi leo urna molestie at elementum eu facilisis sed. Donec pretium vulputate sapien nec sagittis. Feugiat sed lectus vestibulum mattis ullamcorper velit sed ullamcorper morbi. Imperdiet nulla malesuada pellentesque elit eget gravida cum sociis. Donec enim diam vulputate ut pharetra sit amet aliquam id. Nunc id cursus metus aliquam eleifend mi. Urna nec tincidunt praesent semper.

Pharetra pharetra massa massa ultricies. Mollis aliquam ut porttitor leo a diam sollicitudin tempor. Venenatis cras sed felis eget velit aliquet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames. Integer enim neque volutpat ac tincidunt vitae semper quis. Sem integer vitae justo eget magna. Tortor posuere ac ut consequat semper viverra nam. Id donec ultrices tincidunt arcu non sodales neque sodales. Massa massa ultricies mi quis hendrerit dolor magna. Faucibus purus in massa tempor nec feugiat nisl. Vitae turpis massa sed elementum tempus egestas. Odio morbi quis commodo odio aenean sed adipiscing. Non diam phasellus vestibulum lorem sed. Malesuada nunc vel risus commodo viverra maecenas accumsan lacus vel. Integer quis auctor elit sed vulputate mi sit. Id interdum velit laoreet id donec ultrices tincidunt arcu. Sit amet porttitor eget dolor morbi. Sed augue lacus viverra vitae. Facilisis gravida neque convallis a. Donec ac odio tempor orci dapibus.

Semper auctor neque vitae tempus quam pellentesque nec nam. Arcu cursus vitae congue mauris rhoncus aenean. Dignissim cras tincidunt lobortis feugiat vivamus at augue. Et tortor consequat id porta nibh venenatis. Sagittis id consectetur purus ut. Dictum at tempor commodo ullamcorper a lacus vestibulum. Tempor orci eu lobortis elementum nibh tellus molestie nunc. Dui nunc mattis enim ut. Volutpat est velit egestas dui id. Mauris pharetra et ultrices neque ornare aenean euismod. Cursus euismod quis viverra nibh. Dapibus ultrices in iaculis nunc sed augue.
"""

class SessionTimeoutException(Exception):
	pass

class Chunk:
	def __init__(self, seq, header, data=b''):
		self.seq = seq
		self.raw = header.encode('utf-8') + data
		self.eof = len(data) == 0

class Response:
	def __init__(self, mime_type, f):
		self.mime_type = mime_type
		self.seq = random.randint(20000, 65536)
		self.start = self.seq
		self.f = f
		self.chunks = []
		self.eof = None

	def close(self):
		self.f.close()

	def __iter__(self):
		self.pos = 0
		return self

	def __next__(self):
		if self.pos < len(self.chunks):
			seq, chunk = self.chunks[self.pos]
			self.pos += 1
			return seq, chunk

		if self.eof:
			raise StopIteration()

		data = self.f.read(chunk_size)

		self.seq += 1
		logging.debug(f"Building chunk {self.seq}")

		if not data:
			chunk = Chunk(self.seq, f"{self.seq}\r\n")
			self.eof = self.seq
		elif self.mime_type:
			chunk = Chunk(self.seq, f"{self.seq} {self.mime_type}\r\n", data)
			self.mime_type = None
		else:
			chunk = Chunk(self.seq, f"{self.seq}\r\n", data)

		self.chunks.append((self.seq, chunk))
		self.pos += 1
		return self.seq, chunk

	def ack(self, seq):
		self.chunks = [(oseq, chunk) for oseq, chunk in self.chunks if oseq != seq]

	def sent(self):
		return self.eof and not self.chunks

class Session:
	def __init__(self, sock, src, mime_type, f, chunk_size):
		self.sock = sock
		self.src = src
		self.mime_type = mime_type
		self.sent = {}
		self.started = time.time()

		self.response = Response(mime_type, f)

	def close(self):
		self.response.close()

	def send(self):
		if time.time() > self.started + 30:
			raise SessionTimeoutException()

		unacked = 0

		now = time.time()
		for seq, chunk in self.response:
			sent = self.sent.get(seq, 0)
			if sent < now - 2:
				if sent:
					logging.info(f"Re-sending {seq} ({unacked}/8) to {self.src}")
				else:
					logging.info(f"Sending {seq} ({unacked}/8) to {self.src}")
				self.sock.sendto(chunk.raw, self.src)
				self.sent[seq] = now

			# allow only 8 chunks awaiting acknowledgement at a time
			unacked += 1
			if unacked == 8:
				break

	def ack(self, seq):
		if seq not in self.sent:
			raise Exception(f"Unknown packet for {self.src}: {seq}")

		logging.info(f"{self.src} has received {seq}")
		self.response.ack(seq)

		return self.response.sent()

logging.basicConfig(level=logging.INFO)

sock = socket.socket(type=socket.SOCK_DGRAM)
sock.bind(('', 6775))

sessions = collections.OrderedDict()
while True:
	ready, _, _ = select.select([sock.fileno()], [], [], 0.1)

	finished = []

	if ready:
		pkt, src = sock.recvfrom(2048)
		if pkt.endswith(b'\r\n'):
			try:
				session = sessions.get(src)
				if session:
					try:
						seq = int(pkt[:len(pkt) - 2])
					except ValueError as e:
						# probably a duplicate request packet packet
						logging.exception("Received invalid packet", e)
					else:
						if session.ack(seq):
							logging.info(f"Session {src} has ended successfully")
							finished.append(src)
				else:
					if len(sessions) > 32:
						raise Exception("Too many sessions")

					if pkt.startswith(b'guppy://'):
						url = urlparse(pkt.decode('utf-8'))

						mime_type = "text/gemini"
						chunk_size = 512

						if url.path == '' or url.path == '/':
							f = io.BytesIO(home.encode('utf-8'))
							chunk_size = 512
						elif url.path == '/lorem':
							f = io.BytesIO(lorem_ipsum.encode('utf-8'))
						elif url.path == '/echo':
							mime_type = "text/plain"
							data = unquote(url.query).encode('utf-8')
							if not data:
								sock.sendto(b'1 Your name\r\n', src)
								raise Exception("Your name")

							f = io.BytesIO(data)
						elif url.path == '/rick.mp4':
							mime_type = "video/mp4"
							f = open('/tmp/rick.mp4', 'rb')
							chunk_size = 2048
						else:
							raise Exception(f"Invalid path")

						sessions[src] = Session(sock, src, mime_type, f, chunk_size)
			except Exception as e:
				logging.exception("Unhandled exception", e)

	for src, session in sessions.items():
		try:
			session.send()
		except SessionTimeoutException:
			logging.info(f"Session {src} has timed out")
			finished.append(src)
		except Exception as e:
			logging.exception("Unhandled exception", e)

	for src in finished:
		sessions[src].close()
		sessions.pop(src)