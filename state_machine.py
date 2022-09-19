from transitions import Machine
from models import UserState


_transitions = [
    {'trigger': 'set_first_name', 'source': UserState.COLLECTING_FIRST_NAME, 'dest': UserState.COLLECTING_LAST_NAME},
    {'trigger': 'set_last_name', 'source': UserState.COLLECTING_LAST_NAME, 'dest': UserState.COLLECTING_PHONE},
    {'trigger': 'set_phone', 'source': UserState.COLLECTING_PHONE, 'dest': UserState.COLLECTING_RTSF_URL},
    {'trigger': 'set_rtsf_url', 'source': UserState.COLLECTING_RTSF_URL, 'dest': UserState.IN_REVIEW},
    {'trigger': 'accept', 'source': UserState.IN_REVIEW, 'dest': UserState.ACCEPTED},
    {'trigger': 'reject', 'source': UserState.IN_REVIEW, 'dest': UserState.REJECTED},
    {'trigger': 'start_vote', 'source': UserState.ACCEPTED, 'dest': UserState.VOTING},
    {'trigger': 'save_vote_result', 'source': UserState.VOTING, 'dest': UserState.VOTED},
]


class UserStateMachine:
    def __init__(self, state: UserState) -> None:
        self._machine = Machine(
            model=self,
            states=UserState,
            transitions=_transitions,
            initial=state,
        )

    @staticmethod
    def get_initial_state() -> UserState:
        return UserState.COLLECTING_FIRST_NAME
