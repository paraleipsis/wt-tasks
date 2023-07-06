## wt-tasks

1. Распишите пример(ы) unit тестов на эту функцию:

```python
async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)
```

Решение в модуле test_docker_logs.py.

2. Напишите эндпойнт, который в качестве параметра сможет принимать незакодированную (unencoded) ссылку и возвращать его закодированным.

Решение в модуле encode_app.py.
