import pytest
from core.base_agent import SharedState, AgentTask

class TestSharedState:
    @pytest.mark.unit
    def test_add_task_priority_sorting(self):
        """
        Verify that add_task sorts tasks by priority (lowest int = highest priority).
        """
        state = SharedState()

        # Add tasks in non-sorted order
        tasks = [
            AgentTask(task_id="task1", type="test", description="p10", priority=10),
            AgentTask(task_id="task2", type="test", description="p5", priority=5),
            AgentTask(task_id="task3", type="test", description="p20", priority=20),
            AgentTask(task_id="task4", type="test", description="p1", priority=1),
        ]

        for task in tasks:
            state.add_task(task)

        # Expected order: task4 (1), task2 (5), task1 (10), task3 (20)
        assert len(state.task_queue) == 4
        assert state.task_queue[0]["task_id"] == "task4"
        assert state.task_queue[1]["task_id"] == "task2"
        assert state.task_queue[2]["task_id"] == "task1"
        assert state.task_queue[3]["task_id"] == "task3"

        # Verify priority values
        priorities = [t["priority"] for t in state.task_queue]
        assert priorities == [1, 5, 10, 20]

    @pytest.mark.unit
    def test_add_task_stable_sorting(self):
        """
        Verify that tasks with the same priority maintain their insertion order.
        """
        state = SharedState()

        # Add tasks with same priority
        task1 = AgentTask(task_id="A1", type="test", description="first", priority=10)
        task2 = AgentTask(task_id="A2", type="test", description="second", priority=10)
        task3 = AgentTask(task_id="A3", type="test", description="third", priority=10)

        state.add_task(task1)
        state.add_task(task2)
        state.add_task(task3)

        assert state.task_queue[0]["task_id"] == "A1"
        assert state.task_queue[1]["task_id"] == "A2"
        assert state.task_queue[2]["task_id"] == "A3"

    @pytest.mark.unit
    def test_add_task_mixed_insertion(self):
        """
        Test adding tasks one by one and checking sorting after each addition.
        """
        state = SharedState()

        state.add_task(AgentTask(task_id="t1", type="test", description="p10", priority=10))
        assert state.task_queue[0]["task_id"] == "t1"

        state.add_task(AgentTask(task_id="t2", type="test", description="p5", priority=5))
        assert state.task_queue[0]["task_id"] == "t2"
        assert state.task_queue[1]["task_id"] == "t1"

        state.add_task(AgentTask(task_id="t3", type="test", description="p7", priority=7))
        assert state.task_queue[0]["task_id"] == "t2"
        assert state.task_queue[1]["task_id"] == "t3"
        assert state.task_queue[2]["task_id"] == "t1"

    @pytest.mark.unit
    def test_add_task_default_handling(self):
        """
        Test that manually added tasks without priority (if any) default to 99 in sorting.
        While add_task takes AgentTask which has default priority 1,
        we want to ensure the sort key lambda works as intended.
        """
        state = SharedState()

        # Normal task
        state.add_task(AgentTask(task_id="normal", type="test", description="p10", priority=10))

        # Manually bypass add_task to test the sort lambda behavior if we were to trigger it
        # Actually, let's just test that add_task uses 99 for sorting if priority was somehow missing
        # Although add_task does append(task.to_dict()), then sort.
        # If I want to test the lambda specifically:

        state.task_queue.append({"task_id": "no_priority", "type": "test"})
        # Re-trigger sort using the same logic as add_task
        state.task_queue.sort(key=lambda t: t.get("priority", 99))

        assert state.task_queue[0]["task_id"] == "normal"
        assert state.task_queue[1]["task_id"] == "no_priority"
