# ruff: noqa: INP001, T201, COM812
import argparse
import asyncio
import codecs
import functools


async def handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, *, encoding: str
):
    addr = writer.get_extra_info("peername")
    print(f"Connect: {addr!r}")

    decoder = codecs.getincrementaldecoder(encoding)()
    while True:
        if (data := await reader.read(1)) == b"":
            break
        mes = decoder.decode(data)
        print(mes, end="")

        writer.write(data)
        await writer.drain()
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
