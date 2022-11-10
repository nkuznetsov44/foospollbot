from transitions import Machine
from models.entities import UserInfo, UserState


_transitions = [
    {
        "trigger": "next",
        "source": UserState.COLLECTING_FIRST_NAME,
        "dest": UserState.COLLECTING_LAST_NAME,
    },
    {
        "trigger": "next",
        "source": UserState.COLLECTING_LAST_NAME,
        "dest": UserState.COLLECTING_PHONE,
    },
    {
        "trigger": "next",
        "source": UserState.COLLECTING_PHONE,
        "dest": UserState.COLLECTING_RTSF_URL,
    },
    {
        "trigger": "next",
        "source": UserState.COLLECTING_RTSF_URL,
        "dest": UserState.COLLECTING_PHOTO,
    },
    {
        "trigger": "next",
        "source": UserState.COLLECTING_PHOTO,
        "dest": UserState.IN_REVIEW,
    },
    {
        "trigger": "approve",
        "source": UserState.IN_REVIEW,
        "dest": UserState.ACCEPTED,
        "conditions": "has_full_info",
    },
    {"trigger": "reject", "source": UserState.IN_REVIEW, "dest": UserState.REJECTED},
    {"trigger": "start_vote", "source": UserState.ACCEPTED, "dest": UserState.VOTING},
    {"trigger": "vote_result", "source": UserState.VOTING, "dest": UserState.VOTED},
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

    def has_full_info(self, user_info: UserInfo) -> bool:
        return all(
            (
                user_info.first_name is not None,
                user_info.last_name is not None,
                user_info.phone is not None,
                user_info.rtsf_url is not None,
                user_info.evks_player_id is not None,
                user_info.photo_id is not None,
            )
        )
