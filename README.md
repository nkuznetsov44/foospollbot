# Foos Poll Bot

## Steps to start
- Start postgres database
- Create database, user, grant permissions
- Create `foospollbot/settings/settings.yaml` file from template
- Create and activate python env `python3 -m venv env && . ./env/bin/activate`
- Install deps `pip install -r requirements.txt`
- Create `foospollbot/data/evks_players.csv` file with evks players info
- Set up database `python create_schema.py`
- Run the bot `python foospollbot/bot.py`

## Testing and codestyle
- `export PYTHONPATH=$(pwd)/foospollbot`
- `pytest .`
- Autoformat `black .`
- Check style `flake8 .`

## Select collected applications in review
```
select  tu.id as telegram_user_id,
        tu.first_name as telegram_first_name,
        tu.last_name as telegram_last_name,
        tu.username as telegram_username,
        ui.first_name,
        ui.last_name,
        ui.phone,
        ui.rtsf_url,
        ep.first_name as evks_first_name,
        ep.last_name as evks_last_name,
        ep.foreigner as is_foreigner,
        ep.last_competition_date
from telegram_users tu
join user_infos ui
    on tu.id = ui.telegram_user_id
    and ui.state = 'IN_REVIEW'
left join evks_players ep on ui.evks_player_id = ep.id;
```
