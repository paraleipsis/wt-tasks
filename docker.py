from typing import List

import aiohttp
from aiodocker import DockerError, Docker


async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)


async def run_container(
        name: str,
        image: str,
        tag: str,
        cmd: List[str],
        docker: Docker
):
    config = {
        'Cmd': cmd,
        'Image': f'{image}:{tag}',
    }

    try:
        container = await docker.containers.create(
            config=config,
            name=name
        )
    except DockerError as err:
        await docker.images.pull(from_image=image, tag=tag)
        container = await docker.containers.create(
            config=config,
            name=name
        )
    await container.start()

    return container
