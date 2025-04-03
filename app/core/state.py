"""
State machine implementation for tracking process flows.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class State:
    """
    Representasi dari sebuah state dalam state machine.
    """

    def __init__(self, name: str, data: Optional[Dict[str, Any]] = None):
        """
        Initialize a state.

        Args:
            name: Nama state
            data: Data tambahan yang disimpan dengan state
        """
        self.name = name
        self.data = data or {}

    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"State({self.name})"


class Transition:
    """
    Representasi transisi antar states.
    """

    def __init__(
        self,
        source: State,
        target: State,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        action: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Initialize a transition.

        Args:
            source: State asal
            target: State tujuan
            condition: Fungsi yang menentukan apakah transisi valid
            action: Fungsi yang dieksekusi saat transisi terjadi
        """
        self.source = source
        self.target = target
        self.condition = condition
        self.action = action

    def is_valid(self, context: Dict[str, Any]) -> bool:
        """Check if transition is valid with given context."""
        if self.condition is None:
            return True
        return self.condition(context)

    def execute(self, context: Dict[str, Any]) -> None:
        """Execute transition action."""
        if self.action:
            self.action(context)


class StateMachine:
    """
    State machine untuk tracking dan manajemen alur proses.
    """

    def __init__(self, initial_state: State):
        """
        Initialize state machine.

        Args:
            initial_state: State awal
        """
        self.initial_state = initial_state
        self.current_state = initial_state
        self.states: Set[State] = {initial_state}
        self.transitions: Dict[State, List[Transition]] = {}
        self.context: Dict[str, Any] = {}
        self.history: List[
            Tuple[State, State, Dict[str, Any]]
        ] = []  # (from, to, context)

    def add_state(self, state: State) -> None:
        """
        Add a state to the state machine.

        Args:
            state: State yang akan ditambahkan
        """
        self.states.add(state)

    def add_transition(self, transition: Transition) -> None:
        """
        Add a transition to the state machine.

        Args:
            transition: Transisi yang akan ditambahkan
        """
        if transition.source not in self.states:
            self.add_state(transition.source)

        if transition.target not in self.states:
            self.add_state(transition.target)

        if transition.source not in self.transitions:
            self.transitions[transition.source] = []

        self.transitions[transition.source].append(transition)

    def get_available_transitions(self) -> List[Transition]:
        """
        Get all available transitions from current state.

        Returns:
            List of available transitions
        """
        if self.current_state not in self.transitions:
            return []

        available = []
        for transition in self.transitions[self.current_state]:
            if transition.is_valid(self.context):
                available.append(transition)

        return available

    def can_transition_to(self, target_state_name: str) -> bool:
        """
        Check if can transition to a target state.

        Args:
            target_state_name: Nama state tujuan

        Returns:
            True if transition is possible, False otherwise
        """
        for transition in self.get_available_transitions():
            if transition.target.name == target_state_name:
                return True
        return False

    def transition_to(self, target_state_name: str) -> bool:
        """
        Transition to a target state if possible.

        Args:
            target_state_name: Nama state tujuan

        Returns:
            True if transition successful, False otherwise
        """
        for transition in self.get_available_transitions():
            if transition.target.name == target_state_name:
                old_state = self.current_state

                # Execute transition action
                transition.execute(self.context)

                # Update state
                self.current_state = transition.target

                # Record in history
                self.history.append(
                    (old_state, self.current_state, self.context.copy())
                )

                logger.info(
                    f"Transitioned from {old_state.name} to {self.current_state.name}"
                )
                return True

        logger.warning(
            f"Cannot transition from {self.current_state.name} to {target_state_name}"
        )
        return False

    def reset(self) -> None:
        """Reset state machine to initial state."""
        old_state = self.current_state
        self.current_state = self.initial_state
        self.context = {}
        self.history.append((old_state, self.current_state, self.context.copy()))
        logger.info(f"Reset state machine to {self.initial_state.name}")
