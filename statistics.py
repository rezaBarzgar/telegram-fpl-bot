import json
import requests
import pandas as pd

import utils

"""EXAMPLE OF AN ELEMENT's DATA



'chance_of_playing_next_round': None,
  'chance_of_playing_this_round': None,
  'code': 80201,
  'cost_change_event': 0,
  'cost_change_event_fall': 0,
  'cost_change_start': 0,
  'cost_change_start_fall': 0,
  'dreamteam_count': 0,
  'element_type': 1,
  'ep_next': '3.5',
  'ep_this': None,
  'event_points': 0,
  'first_name': 'Bernd',
  'form': '0.0',
  'id': 1,
  'in_dreamteam': False,
  'news': '',
  'news_added': None,
  'now_cost': 50,
  'photo': '80201.jpg',
  'points_per_game': '3.7',
  'second_name': 'Leno',
  'selected_by_percent': '2.3',
  'special': False,
  'squad_number': None,
  'status': 'a',
  'team': 1,
  'team_code': 3,
  'total_points': 131,
  'transfers_in': 0,
  'transfers_in_event': 0,
  'transfers_out': 0,
  'transfers_out_event': 0,
  'value_form': '0.0',
  'value_season': '26.2',
  'web_name': 'Leno',
  'minutes': 3131,
  'goals_scored': 0,
  'assists': 0,
  'clean_sheets': 11,
  'goals_conceded': 37,
  'own_goals': 1,
  'penalties_saved': 1,
  'penalties_missed': 0,
  'yellow_cards': 0,
  'red_cards': 1,
  'saves': 86,
  'bonus': 11,
  'bps': 625,
  'influence': '702.2',
  'creativity': '0.0',
  'threat': '2.0',
  'ict_index': '70.3',
  'influence_rank': 42,
  'influence_rank_type': 12,
  'creativity_rank': 434,
  'creativity_rank_type': 46,
  'threat_rank': 327,
  'threat_rank_type': 4,
  'ict_index_rank': 198,
  'ict_index_rank_type': 13,
  'corners_and_indirect_freekicks_order': None,
  'corners_and_indirect_freekicks_text': '',
  'direct_freekicks_order': None,
  'direct_freekicks_text': '',
  'penalties_order': None,
  'penalties_text': ''
"""


class Statistics:
    def __init__(self):
        self.base_urls = ['https://fantasy.premierleague.com/api/bootstrap-static/',
                          'https://fantasy.premierleague.com/api/element-summary/']
        self.necessary_statistics = [
            'dreamteam_count',
            'element_type',
            'ep_next',
            'ep_this',
            'event_points',
            'first_name',
            'form',
            'in_dreamteam',
            'now_cost',
            'points_per_game',
            'second_name',
            'selected_by_percent',
            'status',
            'team',
            'total_points',
            'transfers_in_event',
            'transfers_out_event',
            'web_name',
            'minutes',
            'goals_scored',
            'assists',
            'clean_sheets',
            'goals_conceded',
            'own_goals',
            'penalties_saved',
            'penalties_missed',
            'yellow_cards',
            'red_cards',
            'saves',
            'bonus',
            'ict_index',
            'ict_index_rank',
        ]

    def update_statistics(self):
        # TODO chand ta az value ha bayad az str tabdil be int beshe
        req = requests.get(self.base_urls[0])
        print('received')
        data = req.json()['elements']
        teams_dict = self.__get_teams_name(req)
        elements_type_dict = self.__get_element_types(req)
        keys = data[0].keys()
        output = []
        for player in data:
            temp = {}
            for key in keys:
                if key in self.necessary_statistics:
                    temp[key] = player[key]
            temp['selected_by_percent'] = float(temp['selected_by_percent'])
            temp['team'] = teams_dict[f'{str(player["team"])}']
            temp['element_type'] = elements_type_dict[f'{str(player["element_type"])}']
            temp['web_name'] = utils.strip_accents(temp['web_name']).lower()
            output.append(temp)
        return output

    def __get_teams_name(self, req):
        data = req.json()['teams']
        output = {}
        for item in data:
            output[f'{item["id"]}'] = item['name']
        return output

    def __get_element_types(self, req):
        data = req.json()['element_types']
        output = {}
        for item in data:
            output[f'{item["id"]}'] = item['singular_name']
        return output


if __name__ == '__main__':
    sts = Statistics()
    df = pd.DataFrame(sts.update_statistics())
    # print(type(df[df.web_name == 'salah'].selected_by_percent.item()))
    df = df.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Midfielder'].head().reset_index()
    for index, row in df.iterrows():
        print(f'player {index}: {row.web_name}')
