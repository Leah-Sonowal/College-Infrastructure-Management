import re

ALLOWED_STATUSES = {
    'Pending', 'Under Review', 'Scheduled',
    'In Progress', 'Resolved', 'Closed', 'Escalated'
}

ALLOWED_CATEGORIES = {
    'Electrical', 'Plumbing', 'Furniture',
    'Network', 'Cleanliness', 'Structural', 'Other'
}

ALLOWED_ROLES = {'Student', 'Faculty', 'Staff', 'Technician', 'Admin'}


def validate_email(email: str) -> bool:
    """Check basic email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return bool(re.match(pattern, email))


def validate_registration(data: dict) -> list[str]:
    """Return a list of validation error messages for registration."""
    errors = []

    for field in ('first_name', 'last_name', 'email', 'password', 'user_type', 'date_of_birth'):
        if not data.get(field):
            errors.append(f"'{field}' is required.")

    if data.get('email') and not validate_email(data['email']):
        errors.append("Invalid email format.")

    if data.get('password') and len(data['password']) < 6:
        errors.append("Password must be at least 6 characters.")

    if data.get('user_type') and data['user_type'] not in ALLOWED_ROLES:
        errors.append(f"user_type must be one of: {', '.join(ALLOWED_ROLES)}.")

    return errors


def validate_issue(data: dict) -> list[str]:
    """Return a list of validation error messages for issue creation."""
    errors = []

    if not data.get('description'):
        errors.append("'description' is required.")

    if not data.get('issue_category'):
        errors.append("'issue_category' is required.")
    elif data['issue_category'] not in ALLOWED_CATEGORIES:
        errors.append(f"issue_category must be one of: {', '.join(ALLOWED_CATEGORIES)}.")

    if data.get('status') and data['status'] not in ALLOWED_STATUSES:
        errors.append(f"status must be one of: {', '.join(ALLOWED_STATUSES)}.")

    return errors


def validate_status_update(data: dict) -> list[str]:
    """Validate a status update payload."""
    errors = []
    status = data.get('status')
    if not status:
        errors.append("'status' is required.")
    elif status not in ALLOWED_STATUSES:
        errors.append(f"status must be one of: {', '.join(ALLOWED_STATUSES)}.")
    return errors
