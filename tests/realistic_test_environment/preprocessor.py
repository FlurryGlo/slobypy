import asyncio
from pathlib import Path

css_process = None
css_event = asyncio.Event()


async def init() -> dict:
    global css_process

    css_process = await asyncio.create_subprocess_shell(
        "npx tailwindcss -i ./css/input.css -o ./css/output.css --watch",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    return {
        "process_css": process_css,
        "tasks": [_read_css_stream(css_process.stderr)]
    }


async def _read_css_stream(stream):
    while True:
        line = await stream.readline()
        if line:
            if line.startswith(b"Rebuilding..."):
                css_event.clear()
            elif line.startswith(b"Done in"):
                css_event.set()
        else:
            break


async def process_css() -> Path:
    global css_event
    await css_event.wait()
    return Path("css/output.css")
