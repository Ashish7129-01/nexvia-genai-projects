
# Role-Based Access Control (RBAC)
ADMIN = "admin"
EMPLOYEE = "employee"

VALID_ROLES = {ADMIN, EMPLOYEE}


def can_access_document(user_role, document):
    """
    Check whether a user can access a document.
    """

    if user_role not in VALID_ROLES:
        return False

    # Documents without permission metadata are denied.
    allowed_roles = document.get("allowed_roles")

    if not isinstance(allowed_roles, list):
        return False

    return user_role in allowed_roles


def filter_documents_by_role(documents, user_role):
    """
    Return only documents accessible to the user.
    """

    return [
        document
        for document in documents
        if can_access_document(user_role, document)
    ]
