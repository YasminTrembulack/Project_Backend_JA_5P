from datetime import datetime
from uuid import uuid4

from app.models.user import User


def test_to_dict():
    test_uuid = uuid4()
    user = User(
        id=test_uuid,
        full_name='User Test',
        created_at=datetime(2024, 3, 25, 12, 0, 0),
    )

    expected_dict = {
        'id': str(test_uuid),
        'full_name': 'User Test',
        'created_at': '2024-03-25T12:00:00',
    }

    assert expected_dict.items() <= user.to_dict().items()


def test_to_dict_exclude():
    test_uuid = uuid4()
    user = User(
        id=test_uuid,
        full_name='User Test',
        created_at=datetime(2024, 3, 25, 12, 0, 0),
    )

    result = user.to_dict(exclude=['created_at'])

    assert 'created_at' not in result
    expected_subset = {'id': str(test_uuid), 'full_name': 'User Test'}
    assert expected_subset.items() <= result.items()
