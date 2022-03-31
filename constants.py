from enum import Enum


class TransactionType(Enum):
    admin_manual = 1
    reaction_good = 2
    reaction_bad = 3
    birthday_wish = 4
    ta_approved = 5
    receive_good_rep = 6
    invalid_name_change = 7
    play_game = 8
    mention_1984 = 9
    profanity = 10
    revert_transaction = 11
    judge_manual = 12
    timeout = 13
    escape_attempt = 14
    emotions = 15
    staff_approved = 16
    staff_disapproved = 17

