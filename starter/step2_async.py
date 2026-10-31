"""Шаг 2. Переписываем на asyncio.

Задание 2а:
  1. Сделайте work корутиной (async def).
  2. Замените time.sleep на await asyncio.sleep.
  3. Сделайте main корутиной и вызовите в ней work через await в цикле.
  4. Запустите через asyncio.run.

Замерьте время. Изменилось ли оно по сравнению с шагом 1? Почему? 
Time elapsed: 10.11s. 
Время не уменьшилось, потому что await подряд создаёт задачи по одной, поэтому в момент ожидания текущей задачи других ещё не существует, значит, event loop нечего запускать и он просто ждёт таймер

Задание 2б:
  Перепишите main так, чтобы все 10 задач ждали одновременно.
  Подсказка: asyncio.gather. Что изменилось в порядке вывода?
"""

import asyncio

from timer import print_time


async def work(n):
    print(f"start {n}")
    await asyncio.sleep(1)
    print(f"done {n}")


async def main():
    coroutines = [work(n) for n in range(1, 11)]
    await asyncio.gather(*coroutines)


if __name__ == "__main__":
    with print_time():
        asyncio.run(main())
