"""Шаг 4 (дополнительный). Блокировка event loop.

Ниже готовый асинхронный сервер из шага 3б. Но теперь клиент "bob"
прислал не запрос в базу, а задачу на тяжёлые вычисления: функция
heavy_compute. Она синхронная и работает 1-3 секунды в зависимости от машины.

Задание 4а:
  В handle_request для клиента "bob" вызовите heavy_compute()
  вместо await asyncio.sleep(duration). Остальные клиенты по-прежнему
  ждут через asyncio.sleep. Запустите.
  Что произошло с остальными клиентами? Почему, ведь всё написано на async?

[  0.0s] alice: запрос принят
[  0.0s] bob: запрос принят
[  7.2s] bob: ответ отправлен
[  7.2s] carol: запрос принят
[  7.2s] dave: запрос принят
[  7.2s] eve: запрос принят
[  7.2s] alice: ответ отправлен
[  7.7s] dave: ответ отправлен
[  7.7s] carol: ответ отправлен
[  7.7s] eve: ответ отправлен
Time elapsed: 7.69s

Хотя программа написана с использованием async, 
синхронная функция heavy_compute() блокирует event loop. 
Она не уступает управление, 
поэтому остальные корутины не могут выполняться до завершения вычислений Bob. 
async сам по себе не делает синхронный код неблокирующим.

Задание 4б:
  Исправьте так, чтобы остальные клиенты не ждали bob. Два инструмента:
    await asyncio.to_thread(heavy_compute)
    await loop.run_in_executor(pool, heavy_compute)
  где loop = asyncio.get_running_loop(), а pool — это ProcessPoolExecutor
  из concurrent.futures, открытый через with в main.
  Попробуйте оба. Порядок строк в выводе должен стать как в шаге 3б,
  время bob зависит от машины.

await asyncio.to_thread(heavy_compute):
[  0.0s] alice: запрос принят
[  0.0s] bob: запрос принят
[  0.0s] carol: запрос принят
[  0.0s] dave: запрос принят
[  0.0s] eve: запрос принят
[  0.5s] alice: ответ отправлен
[  0.5s] carol: ответ отправлен
[  0.5s] dave: ответ отправлен
[  0.6s] eve: ответ отправлен
[  6.4s] bob: ответ отправлен
Time elapsed: 6.38s

await loop.run_in_executor(pool, heavy_compute):
[  0.0s] alice: запрос принят
[  0.0s] bob: запрос принят
[  0.0s] carol: запрос принят
[  0.0s] dave: запрос принят
[  0.0s] eve: запрос принят
[  0.5s] alice: ответ отправлен
[  0.5s] carol: ответ отправлен
[  0.5s] dave: ответ отправлен
[  0.6s] eve: ответ отправлен
[  4.9s] bob: ответ отправлен
Time elapsed: 4.88s

Задание 4в (если осталось время):
  Сделайте тяжёлыми трёх клиентов: bob, dave и eve. Сравните общее время
  для to_thread и для пула процессов. Почему оно отличается? Вспомните GIL.
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor

from timer import log, print_time

CLIENTS = [
    ("alice", 0.5),
    ("bob", 5.0),
    ("carol", 0.5),
    ("dave", 0.5),
    ("eve", 0.5),
]


def heavy_compute() -> int:
    """Синхронные тяжёлые вычисления, 1-3 секунды."""
    h = 0
    for i in range(30_000_000):
        h = (h * 31 + i) & 0xFFFFFFFF
    return h


async def handle_request(client: str, duration: float, pool) -> None:
    log(f"{client}: запрос принят")
    if client == "bob":
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(pool, heavy_compute)
    else:
        await asyncio.sleep(duration)
    log(f"{client}: ответ отправлен")


async def main() -> None:
    with ProcessPoolExecutor() as pool:
        coroutines = [
            handle_request(client, duration, pool)
            for client, duration in CLIENTS
        ]
        await asyncio.gather(*coroutines)


if __name__ == "__main__":
    with print_time():
        asyncio.run(main())
