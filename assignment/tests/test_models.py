"""Unit tests for Task models and field validators.

These tests hit the Pydantic/SQLModel layer directly — no HTTP, no database.
They validate business rules: field constraints, default values, and the
title validator (strip whitespace, reject blank).
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from task_api.models import Task, TaskCreate, TaskUpdate


class TestTaskCreateValidation:
    """TaskCreate is the POST request schema — title is the only required field."""

    def test_valid_minimal_task(self):
        task = TaskCreate(title="Buy groceries")
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.completed is False

    def test_valid_full_task(self):
        task = TaskCreate(title="Deploy app", description="Push to prod", completed=True)
        assert task.description == "Push to prod"
        assert task.completed is True

    # --- title validator ---

    def test_title_leading_trailing_whitespace_is_stripped(self):
        task = TaskCreate(title="  Clean code  ")
        assert task.title == "Clean code"

    def test_title_whitespace_only_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="     ")

    def test_title_empty_string_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_title_at_max_length_is_accepted(self):
        task = TaskCreate(title="a" * 200)
        assert len(task.title) == 200

    def test_title_exceeds_max_length_raises_validation_error(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="a" * 201)

    def test_title_single_character_is_accepted(self):
        task = TaskCreate(title="x")
        assert task.title == "x"

    # --- defaults ---

    def test_completed_defaults_to_false(self):
        task = TaskCreate(title="Task")
        assert task.completed is False

    def test_description_defaults_to_none(self):
        task = TaskCreate(title="Task")
        assert task.description is None

    def test_completed_can_be_set_true(self):
        task = TaskCreate(title="Task", completed=True)
        assert task.completed is True


class TestTaskUpdateValidation:
    """TaskUpdate is the PUT request schema — every field is optional."""

    def test_empty_update_is_valid(self):
        update = TaskUpdate()
        assert update.title is None
        assert update.description is None
        assert update.completed is None

    def test_title_only_update(self):
        update = TaskUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.completed is None

    def test_completed_only_update(self):
        update = TaskUpdate(completed=True)
        assert update.completed is True
        assert update.title is None

    def test_model_dump_exclude_unset_omits_unset_fields(self):
        """Route uses exclude_unset=True to apply only provided fields."""
        update = TaskUpdate(completed=False)
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"completed": False}
        assert "title" not in dumped
        assert "description" not in dumped

    def test_model_dump_exclude_unset_with_multiple_fields(self):
        update = TaskUpdate(title="New", completed=True)
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"title": "New", "completed": True}


class TestTaskDatabaseModel:
    """Task is the SQLModel table model — tests cover auto-generated defaults."""

    def test_id_defaults_to_none_before_db_insert(self):
        task = Task(title="Task")
        assert task.id is None

    def test_created_at_is_auto_set_to_datetime(self):
        task = Task(title="Task")
        assert isinstance(task.created_at, datetime)

    def test_updated_at_is_auto_set_to_datetime(self):
        task = Task(title="Task")
        assert isinstance(task.updated_at, datetime)

    def test_completed_defaults_false(self):
        task = Task(title="Task")
        assert task.completed is False
