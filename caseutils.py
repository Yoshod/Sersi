import pickle
import shortuuid
import time

CASE_DETAILS_FILE = ("Files/Cases/casedetails.pkl")
CASE_HISTORY_FILE = ("Files/Cases/casehistory.pkl")


def reform_case(unique_id, case_num, target_id, moderator_id, case_channel_id, reason):
    try:
        with open(CASE_DETAILS_FILE, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Reformation", case_num, target_id, moderator_id, case_channel_id, reason, timestamp]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details, file)


def probation_case(unique_id, target_id, initial_moderator_id, approving_moderator_id, reason):
    try:
        with open(CASE_DETAILS_FILE, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Probation", target_id, initial_moderator_id, approving_moderator_id, reason, timestamp]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details, file)


def anon_message_mute_case(unique_id, target_id, moderator_id, reason):
    try:
        with open(CASE_DETAILS_FILE, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Anonymous Message Mute", target_id, moderator_id, reason, timestamp]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details, file)


def slur_case(unique_id, slur_used, report_url, target_id, moderator_id, reason):
    try:
        with open(CASE_DETAILS_FILE, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Slur Usage", slur_used, report_url, target_id, moderator_id, reason, timestamp]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details, file)


def bad_faith_ping_case(unique_id, report_url, target_id, moderator_id, reason):
    try:
        with open(CASE_DETAILS_FILE, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Bad Faith Ping", target_id, report_url, moderator_id, reason, timestamp]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details, file)


def custom_case(unique_id, case_info: list = []):
    try:
        with open(CASE_DETAILS_FILE, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = []
    for case_details in case_info:
        case.append(case_info[case_details])
    case.append(timestamp)
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details, file)


def case_history(member_id, case_type):
    try:
        with open(CASE_HISTORY_FILE, "rb") as file:
            case_history = pickle.load(file)
    except (EOFError, TypeError):
        case_history = {}
        case_history[member_id] = []

    global_case_identifier = str(shortuuid.uuid())
    timestamp = int(time.time())

    try:
        cases = case_history[member_id]
        cases.append([global_case_identifier, case_type, timestamp])
        case_history[member_id] = cases
    except KeyError:
        cases = []
        cases.append([global_case_identifier, case_type, timestamp])
        case_history[member_id] = cases

    with open(CASE_HISTORY_FILE, "wb") as file:
        pickle.dump(case_history, file)

    return global_case_identifier
