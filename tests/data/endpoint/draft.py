from tests import pytest

from data.endpoint.draft import get_draft_dict


def test_get_draft_dict():
    input_data = {'PERSON_ID': 1234,
                  'SEASON': 2000,
                  'ROUND_NUMBER': 2,
                  'ROUND_PICK': 10,
                  'OVERALL_PICK': 40,
                  'TEAM_ID': 1000,
                  'ORGANIZATION': 'test'
                  }

    output = get_draft_dict(input_data)

    assert output ==\
           {'draft_id': '20010001234',
            'player_id': 1234,
            'season': 2001,
            'round_number': 2,
            'round_pick': 10,
            'overall_pick': 40,
            'team_id': 1000,
            'previous_team': 'test'
            }
