import pickle

CASE_DETAILS_FILE = ("Files/Cases/casedetails.pkl")

def reform_case(unique_id, case_num, target_id, moderator_id, case_channel, reason):
    with open(CASE_DETAILS_FILE, "rb") as file:
        case_details = pickle.load(file)
    case = ["Reformation", case_num, target_id, moderator_id, case_channel, reason]
    case_details[unique_id] = case
    with open(CASE_DETAILS_FILE, "wb") as file:
        pickle.dump(case_details)
