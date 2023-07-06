import io
import sys
import ast

import pytest
import aiodocker

from docker import run_container, logs


@pytest.mark.asyncio
async def test_logs_out():
    """
    Checking that the given name matches the name from the output
    and that there is a log output at all.
    """

    test_string = 'test'
    cont_cmd = ['/bin/sh', '-c', f'echo "{test_string}"']
    image = 'busybox'
    image_tag = 'latest'
    cont_name = 'test'

    async with aiodocker.Docker() as docker:
        container = await run_container(
            docker=docker,
            cmd=cont_cmd,
            image=image,
            tag=image_tag,
            name=cont_name
        )

        out = io.StringIO()
        sys.stdout = out
        await logs(cont=container.id, name=cont_name)
        sys.stdout = sys.__stdout__
        logs_out = out.getvalue().split(' ')
        log_byte_string_with_header = ast.literal_eval(logs_out[1])
        """
        Every message start with header. The header contains 
        the information which the stream writes (stdout or stderr). 
        It also contains the size of the associated frame encoded 
        in the last four bytes (uint32). It is encoded on the first eight bytes. Reference: 
        https://docs.docker.com/engine/api/v1.43/#tag/Container/operation/ContainerAttach
        So we dont need first eight bytes.
        """
        log_byte_string = log_byte_string_with_header[8:]
        log_string = log_byte_string.decode()

        await container.delete(force=True)
        await docker.images.delete(name=f'{image}:{image_tag}')

    # compare with input name
    assert logs_out[0] == cont_name
    # remove unnecessary \n and compare with input string
    assert log_string.strip() == test_string


@pytest.mark.asyncio
async def test_stream_logs():
    iterations_amount = 5
    test_string = 'test'
    sh_test = ' '.join(f'{i}' for i in range(1, iterations_amount+1))
    cont_cmd = ['/bin/sh', '-c', f'for i in {sh_test}; do echo "{test_string} $i"; done']
    image = 'busybox'
    image_tag = 'latest'
    cont_name = 'test'

    async with aiodocker.Docker() as docker:
        container = await run_container(
            docker=docker,
            cmd=cont_cmd,
            image=image,
            tag=image_tag,
            name=cont_name
        )

        out = io.StringIO()
        sys.stdout = out
        await logs(cont=container.id, name=cont_name)
        sys.stdout = sys.__stdout__
        # each log line start with given name, so we need to split it
        logs_with_name_out = out.getvalue().split(f'{cont_name} b')
        # remove input name so that there is only a logs output
        logs_out = logs_with_name_out[1:]
        # convert to sting
        last_log_with_header = ast.literal_eval(logs_out[-1])
        # remove header
        last_log = last_log_with_header[8:]

        await container.delete(force=True)
        await docker.images.delete(name=f'{image}:{image_tag}')

    assert len(logs_out) == iterations_amount
    assert last_log.strip() == f'{test_string} {iterations_amount}'
