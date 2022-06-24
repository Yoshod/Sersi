import pickle

CASE_DETAILS_FILE = ("Files/Cases/casedetails.pkl")

def reform_case(unique_id, case_num, target_id, moderator_id, case_channel, reason):
    with open(CASE_DETAILS_FILE, "rb") as file:
        case_details = pickle.load(file)
    case = ["Reformation", case_num, target_id, moderator_id, case_channel, reason]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details)

def probation_case(unique_id, target_id, moderator_id, reason):
    with open(CASE_DETAILS_FILE, "rb") as file:
        case_details = pickle.load(file)
    case = ["Probation", target_id, moderator_id, reason]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details)

def anon_message_mute_case(unique_id, target_id, moderator_id, reason):
    with open(CASE_DETAILS_FILE, "rb") as file:
        case_details = pickle.load(file)
    case = ["Anonymous Message Mute", target_id, moderator_id, reason]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details)

def slur_case(unique_id, slur_used, report_url, target_id, moderator_id, reason):
    with open(CASE_DETAILS_FILE, "rb") as file:
        case_details = pickle.load(file)
    case = ["Slur Usage", slur_used, report_url, target_id, moderator_id, reason]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details)

def bad_faith_ping_case(unique_id, report_url, target_id, moderator_id, reason):
    with open(CASE_DETAILS_FILE, "rb") as file:
        case_details = pickle.load(file)
    case = ["Bad Faith Ping", target_id, report_url, moderator_id, reason]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details)
