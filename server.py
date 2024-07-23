import argparse
import asyncio
import codecs
import functools
import sys


async def ainput():
    return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)


async def listener(reader: asyncio.StreamReader, encoding: str):
    decoder = codecs.getincrementaldecoder(encoding)()
    while True:
        if (data := await reader.read(1)) == b"":
            break
        mes = decoder.decode(data)
        print(mes, end="", flush=True)


async def handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, *, encoding: str
):
    addr = writer.get_extra_info("peername")
    print("Use Ctrl-Z plus Return to exit")
    print(f"Connect: {addr!r}")

    task = asyncio.create_task(listener(reader, encoding))

    while True:
        line = await ainput()
        if not line or task.done():
            break
        writer.write(line.encode(encoding))
        await writer.drain()

    task.cancel()

    writer.close()
    await writer.wait_closed()
    print(f"Disconnect: {addr!r}")


async def amain(host: str, port: int, encoding: str):
    server = await asyncio.start_server(
        functools.partial(handler, encoding=encoding),
        host,
        port,
    )

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()
    print("Exit")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default="8888")
    parser.add_argument("-e", "--encoding", default="utf-8")

    args = parser.parse_args()
    asyncio.run(amain(args.host, args.port, args.encoding))


if __name__ == "__main__":
    main()
