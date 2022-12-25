import pickle
import shortuuid
import time

from baseutils import get_page
from configutils import Configuration


def reform_case(
    config: Configuration,
    unique_id,
    case_num,
    target_id,
    moderator_id,
    case_channel_id,
    reason,
):
    try:
        with open(config.datafiles.casedetails, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = [
        "Reformation",
        case_num,
        target_id,
        moderator_id,
        case_channel_id,
        reason,
        timestamp,
    ]
    case_details[unique_id] = case
    with open(config.datafiles.casedetails, "wb") as file:
        pickle.dump(case_details, file)


def probation_case(
    config: Configuration,
    unique_id,
    target_id,
    initial_moderator_id,
    approving_moderator_id,
    reason,
):
    try:
        with open(config.datafiles.casedetails, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = [
        "Probation",
        target_id,
        initial_moderator_id,
        approving_moderator_id,
        reason,
        timestamp,
    ]
    case_details[unique_id] = case
    with open(config.datafiles.casedetails, "wb") as file:
        pickle.dump(case_details, file)


def anon_message_mute_case(
    config: Configuration, unique_id, target_id, moderator_id, reason
):
    try:
        with open(config.datafiles.casedetails, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Anonymous Message Mute", target_id, moderator_id, reason, timestamp]
    case_details[unique_id] = case
    with open(config.datafiles.casedetails, "wb") as file:
        pickle.dump(case_details, file)


def slur_case(
    config: Configuration, unique_id, slur_used, report_url, target_id, moderator_id
):
    try:
        with open(config.datafiles.casedetails, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Slur Usage", slur_used, report_url, target_id, moderator_id, timestamp]
    case_details[unique_id] = case
    with open(config.datafiles.casedetails, "wb") as file:
        pickle.dump(case_details, file)


def bad_faith_ping_case(
    config: Configuration, unique_id, report_url, target_id, moderator_id
):
    try:
        with open(config.datafiles.casedetails, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = ["Bad Faith Ping", target_id, report_url, moderator_id, timestamp]
    case_details[unique_id] = case
    with open(config.datafiles.casedetails, "wb") as file:
        pickle.dump(case_details, file)


def custom_case(config: Configuration, unique_id, case_info: list = []):
    try:
        with open(config.datafiles.casedetails, "rb") as file:
            case_details = pickle.load(file)
    except EOFError:
        case_details = {}
    timestamp = int(time.time())
    case = []
    for case_detail in case_details:
        case.append(case_detail)
    case.append(timestamp)
    case_details[unique_id] = case
    with open(config.datafiles.casedetails, "wb") as file:
        pickle.dump(case_details, file)


def get_member_cases(config: Configuration, member_id, page, per_page=10):
    with open(config.datafiles.casehistory, "rb") as file:
        case_history = pickle.load(file)

    try:
        entry_list = get_page(case_history[member_id][::-1], page, per_page)
    except KeyError:
        entry_list = ([], 0, 0)
    return entry_list


def case_history(config: Configuration, member_id, case_type):
    try:
        with open(config.datafiles.casehistory, "rb") as file:
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

    with open(config.datafiles.casehistory, "wb") as file:
        pickle.dump(case_history, file)

    return global_case_identifier
