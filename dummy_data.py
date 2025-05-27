from datetime import datetime, timedelta

dummy_notifications = [
    {
        "title": "Welcome to Notification System",
        "message": "Thanks for joining our platform!",
        "priority": "low",
        "scheduled_for": datetime.utcnow(),
        "sender": "system",
        "recipients": ["user1"],
        "created_at": datetime.utcnow(),
        "read_by": []
    },
    {
        "title": "Meeting Reminder",
        "message": "Team meeting at 3 PM",
        "priority": "high",
        "scheduled_for": datetime.utcnow() + timedelta(minutes=5),
        "sender": "calendar",
        "recipients": ["user1", "user2"],
        "created_at": datetime.utcnow(),
        "read_by": []
    },
    {
        "title": "Security Alert",
        "message": "New login from unknown device",
        "priority": "emergency",
        "scheduled_for": datetime.utcnow() + timedelta(minutes=10),
        "sender": "security",
        "recipients": ["user2"],
        "created_at": datetime.utcnow(),
        "read_by": []
    },
    {
        "title": "Weekly Report",
        "message": "Your weekly report is ready",
        "priority": "medium",
        "scheduled_for": datetime.utcnow() + timedelta(minutes=15),
        "sender": "reports",
        "recipients": ["user1", "user3"],
        "created_at": datetime.utcnow(),
        "read_by": []
    },
]
