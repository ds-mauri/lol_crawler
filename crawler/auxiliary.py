def join_list_of_dicts_by_key(left_list, right_list, left_key, right_key):
    """Extend the dictionaries in the left list with keys on the right list

    Example:
    left_list = [
        {'id': 1, 'name': 'Rosana'},
        {'id': 2, 'name': 'Carlos'},
        {'id': 3, 'name': 'Mariana'},
    ]

    right_list = [
        {'id': 1, 'age': 32},
        {'id': 2, 'age': 44},
        {'id': 3, 'age': 28},
    ]
    
    joined_list = [
        {'id': 1, 'name': 'Rosana', 'age': 32},
        {'id': 2, 'name': 'Carlos', 'age': 44},
        {'id': 3, 'name': 'Mariana', 'age': 28},
    ]
    """

    joined_list = []
    for left_dict in left_list:
        left_id = left_dict.get(left_key)
        for right_dict in right_list:
            right_id = right_dict.get(right_key)
            if right_id == left_id:
                left_dict.update(right_dict)
        joined_list.append(left_dict)
    
    return joined_list
