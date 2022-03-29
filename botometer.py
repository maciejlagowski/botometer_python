import requests as req
import json
import PySimpleGUI as sg


def twitter_rest_get(api, params):
    twitter_headers = {'Authorization': 'Bearer twitterTokenHere'}
    return req.get('https://api.twitter.com/1.1/{}'.format(api), params=params, headers=twitter_headers).json()


def get_user_data_twitter(screen_name):
    response = twitter_rest_get('users/show.json', {'screen_name': screen_name})
    if 'errors' in dict(response):
        print(response['errors'])
    else:
        return {'id': response['id'], 'screen_name': screen_name}


def get_user_dump_twitter(user_data):
    params = {'count': 200, 'include_rts': True, 'screen_name': user_data['screen_name'], 'user_id': user_data['id']}
    timeline = twitter_rest_get('statuses/user_timeline.json', params)
    mentions = twitter_rest_get('search/tweets.json', {'q': '@' + user_data['screen_name'], 'count': 100})
    return json.dumps({'user': user_data, 'timeline': timeline, 'mentions': mentions})


def botometer_rest_post(user_dump):
    headers = {'content-type': 'application/json', 'X-RapidAPI-Host': 'botometer-pro.p.rapidapi.com',
               'X-RapidAPI-Key': 'botometerTokenHere'}
    return req.post('https://botometer-pro.p.rapidapi.com/4/check_account', data=user_dump, headers=headers).json()


def check_if_user_is_bot(user_name):
    user_data = get_user_data_twitter(user_name)
    if user_data is None:
        sg.Popup('Botometer', 'Username {} does not exist.'.format(user_name))
    else:
        user_dump = get_user_dump_twitter(user_data)
        res = botometer_rest_post(user_dump)
        print(res)
        if 'raw_scores' in dict(res):
            res2 = dict(res['raw_scores']).get('universal')
            result = 'astroturf = {}\nfake_follower = {}\nfinancial = {}\nother = {}\nself_declared = {}\nspammer = {}\n\noverall = {}'.format(
                res2['astroturf'], res2['fake_follower'], res2['financial'], res2['other'], res2['self_declared'],
                res2['spammer'], res2['overall'])
            sg.Popup(user_name, 'Result: ', result)
        else:
            sg.Popup(user_name, 'Result: ', res)


# main
sg.theme('DarkAmber')
layout = [[sg.Text('Enter twitter username')],
          [sg.Input(key='name')],
          [sg.Button('Check'), sg.Exit()]]
window = sg.Window('Botometer', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if values['name'] != '':
        check_if_user_is_bot(values['name'])
    else:
        sg.popup('User name cannot be empty')
window.close()
