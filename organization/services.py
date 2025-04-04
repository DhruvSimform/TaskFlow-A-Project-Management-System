# organization/services.py
from organization.models import Department


def create_department(validated_data, user):
    """
    Handles the creation of a new department.
    Ensures that `created_by` is set to the authenticated user.
    """
    validated_data["created_by"] = (
        user  # Assign the user who is creating the department
    )
    return Department.objects.create(**validated_data)
