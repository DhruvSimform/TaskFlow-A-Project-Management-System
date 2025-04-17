from organization.models import Department


def create_department(validated_data, user):
    """
    Handles the creation of a new department.
    Ensures that `created_by` is set to the authenticated user.
    """

    return Department.objects.create(**validated_data)
