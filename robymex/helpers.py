from typing import List, Awaitable, Tuple, Any
import asyncio


async def wait_first(coros:List[Awaitable])->Tuple[bool,Any]:
	tasks = [ asyncio.create_task(coro) for coro in coros ]
	done,_ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
	task = done.pop()
	return task is tasks[0], task.result()
