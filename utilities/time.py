# Formats the time as "w weeks, d days, h hours, m minutes and s seconds".
#
# NOTE: chaining calls together is REALLY bad for performance, but this piece of crap language can't really do it differently without shitting itself
def format_time_user_display(seconds: int) -> str:
    if seconds >= 60 ** 2 * 24 * 7:
        result_weeks = int(seconds / (60 ** 2 * 24 * 7))
        output = f"{result_weeks} week{'s' if result_weeks != 1 else ''}"

        result_days = int(seconds % (60 ** 2 * 24 * 7))
        if result_days > 0:
            output += ", " + format_time_user_display(result_days)

        return output

    if seconds >= 60 ** 2 * 24:
        result_days = int(seconds / (60 ** 2 * 24))
        output = f"{result_days} day{'s' if result_days != 1 else ''}"

        result_hours = int(seconds % (60 ** 2 * 24))
        if result_hours > 0:
            output += ", " + format_time_user_display(result_hours)

        return output

    if seconds >= 60 ** 2:
        result_hours = int(seconds / (60 ** 2))
        output = f"{result_hours} hour{'s' if result_hours != 1 else ''}"

        result_minutes = int(seconds % (60 ** 2))
        if result_minutes > 0:
            output += ", " + format_time_user_display(result_minutes)

        return output

    if seconds >= 60:
        result_minutes = int(seconds / 60)
        output = f"{result_minutes} minute{'s' if result_minutes != 1 else ''}"

        result_seconds = int(seconds % 60)
        if result_seconds > 0:
            output += ", " + format_time_user_display(result_seconds)

        return output

    return f"{seconds} second{'s' if seconds != 1 else ''}"
