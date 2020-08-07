import json
import fitbit
import datetime

# ClientId, ClientSecretをjsonで記述する
SECRET_FILE = 'secrets.json'
# curlで取得したtokenを以下のファイルに貼り付ける
TOKEN_FILE = 'tokens.json'


def refresh_token_callback(token):
    with open(TOKEN_FILE, 'w') as f:
        f.write(str(token))
    return

def pound_to_kg(pound):
    kg = pound * 0.454
    return kg


with open(SECRET_FILE, 'r') as f:
    secrets = json.load(f)

with open(TOKEN_FILE, 'r') as f:
    tokens = json.load(f)

# refresh_cbによりtokenを自動で更新する
# これを実行せず、tokenがexpireすると
# 再認証するしかなくなる
client = fitbit.Fitbit(
    secrets['ClientId'],
    secrets['ClientSecret'],
    access_token = tokens['access_token'],
    refresh_token = tokens['refresh_token'],
    refresh_cb = refresh_token_callback)


NOW = datetime.datetime.now()
PERIOD=24
CURR_HOUR= NOW.replace(minute=0, second=0, microsecond=0)
PAST_HOUR = CURR_HOUR + datetime.timedelta(hours=-PERIOD)
base_date = CURR_HOUR.strftime('%Y-%m-%d')
end_time = CURR_HOUR.strftime('%H:%M')

if int(end_time[0:2]) > int(PAST_HOUR.strftime('%H')):
    start_time = PAST_HOUR.strftime('%H:%M')
else:
    start_time = "00:00"

# 心拍
res = client.intraday_time_series(
        'activities/heart',
        base_date=base_date,
        detail_level='1sec',
        start_time=start_time,
        end_time=end_time)

with open(f'output/heart_{base_date}.csv', 'w') as f:
    f.write("timestamp,heart\n")
    for elm in res['activities-heart-intraday']['dataset']:
        f.write(f"{base_date} {elm['time']},{elm['value']}\n")


# 歩数
res = client.intraday_time_series(
        'activities/steps',
        base_date=base_date,
        detail_level='1min',
        start_time=start_time,
        end_time=end_time)

with open(f'output/steps_{base_date}.csv', 'w') as f:
    f.write("timestamp,steps\n")
    for elm in res['activities-steps-intraday']['dataset']:
        f.write(f"{base_date} {elm['time']},{elm['value']}\n")


# 睡眠
res = client.sleep(date=base_date)

with open(f'output/sleep_{base_date}.csv', 'w') as f:
    f.write("timestamp,steps\n")
    for elm in res['sleep'][0]['minuteData']:
        f.write(f"{base_date} {elm['dateTime']},{elm['value']}\n")


# 体重
res = client.get_bodyweight(base_date=base_date)

with open(f'output/weight_{base_date}.csv', 'w') as f:
    f.write("timestamp,weight\n")
    for val in res['weight']:
        f.write("{base_date},{pound_to_kg(val)}\n")

