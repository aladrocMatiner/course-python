import asyncio
import unittest

from structured_async import failing_group, successful_group, timed_group


class StructuredAsyncTests(unittest.IsolatedAsyncioTestCase):
    def assert_no_background_tasks(self) -> None:
        current = asyncio.current_task()
        pending = [
            task
            for task in asyncio.all_tasks()
            if task is not current and not task.done()
        ]
        self.assertEqual([], pending)

    async def test_successful_group_returns_owned_results(self) -> None:
        self.assertEqual(["first:done", "second:done"], await successful_group())
        self.assert_no_background_tasks()

    async def test_child_failure_cancels_and_cleans_sibling(self) -> None:
        events = await failing_group()
        self.assertIn("failure:cleanup", events)
        self.assertIn("sibling:cleanup", events)
        self.assertIn("failure:handled", events)
        self.assert_no_background_tasks()

    async def test_timeout_cancels_and_cleans_group(self) -> None:
        events = await timed_group()
        self.assertIn("slow-a:cleanup", events)
        self.assertIn("slow-b:cleanup", events)
        self.assertIn("timeout:handled", events)
        self.assert_no_background_tasks()


if __name__ == "__main__":
    unittest.main()
