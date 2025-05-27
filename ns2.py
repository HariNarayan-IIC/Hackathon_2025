from datetime import datetime, timedelta

# Rule-based scheduler
def get_schedule_rule_based(category, priority, avg_reaction_time, click_count, dismiss_count):
    # Time window per category
    category_windows = {
        "Work": ("09:00", "17:00"),
        "Finance": ("09:00", "17:00"),
        "System": ("08:00", "16:00"),
        "Social": ("18:00", "22:00"),
        "News": ("07:00", "11:00"),
        "Entertainment": ("20:00", "23:00"),
        "Health": ("07:00", "20:00"),
        "Promotions": ("10:00", "18:00"),
    }

    start_time_str, end_time_str = category_windows.get(category.capitalize(), ("10:00", "18:00"))

    today = datetime.now().date()
    startdatetime = datetime.strptime(f"{today} {start_time_str}", "%Y-%m-%d %H:%M")
    enddatetime = datetime.strptime(f"{today} {end_time_str}", "%Y-%m-%d %H:%M")

    # Priority weight
    priority_weight = {"high": 3, "medium": 2, "low": 1}.get(priority.lower(), 1)

    # Engagement scoring
    score = priority_weight

    if avg_reaction_time is not None:
        if avg_reaction_time < 30:
            score += 2
        elif avg_reaction_time < 60:
            score += 1
        else:
            score -= 1

    if click_count is not None:
        if click_count >= 5:
            score += 2
        elif click_count >= 2:
            score += 1
        else:
            score -= 1

    if dismiss_count is not None:
        if dismiss_count >= 5:
            score -= 2
        elif dismiss_count >= 2:
            score -= 1
        else:
            score += 1

    frequency = max(1, min(score, 5))  # Clamp frequency between 1 and 5

    return {
        "startdatetime": startdatetime.strftime("%Y-%m-%d %H:%M"),
        "\n enddatetime": enddatetime.strftime("%Y-%m-%d %H:%M"),
        "\n frequency": frequency
    }

# Input function
def get_user_input():
    print("\nEnter Notification Info (type 'e' to stop):")

    category = input("Notification category (required): ").strip()
    if category.lower() == "e":
        return None

    while not category:
        category = input("Category is required. Please enter again: ").strip()

    priority = input("Notification priority (required): ").strip()
    while not priority:
        priority = input("Priority is required. Please enter again: ").strip()

    try:
        avg_reaction_time = input("Avg. reaction time in seconds (optional): ").strip()
        avg_reaction_time = int(avg_reaction_time) if avg_reaction_time else None

        click_count = input("Click count (optional): ").strip()
        click_count = int(click_count) if click_count else None

        dismiss_count = input("Dismiss count (optional): ").strip()
        dismiss_count = int(dismiss_count) if dismiss_count else None
    except ValueError:
        print("Invalid input. Optional fields will be ignored.")
        avg_reaction_time = click_count = dismiss_count = None

    return category, priority, avg_reaction_time, click_count, dismiss_count

# Main loop
if __name__ == "__main__":
    while True:
        user_data = get_user_input()
        if user_data is None:
            print("Exiting scheduler.")
            break

        cat, pri, art, cc, dc = user_data
        result = get_schedule_rule_based(cat, pri, art, cc, dc)

        print("\n📅 Suggested Notification Schedule:")
        print(result)
