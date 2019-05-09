from blog.constants import TestType


def get_id_for_form_fields(test_type: TestType, number):
    id_name = '{test_type}_{number}'
    if test_type == TestType.CLOSE.value:
        id_name = id_name.format(test_type=TestType.CLOSE.value, number=number)
    if test_type == TestType.OPEN.value:
        id_name = id_name.format(test_type=TestType.OPEN.value, number=number)

    return id_name
