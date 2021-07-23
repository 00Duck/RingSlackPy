from pathlib import Path
from slack_bot import SlackBot
import traceback
import logging
from time import sleep
from ring_session import RingSession

def main():
    loop_sleep = float(5)
    retries = 0
    max_retries = 5
    rs = RingSession(Path('ring_token.cache'))
    rs.create_ring()
    rs.ring.update_devices()
    bot = SlackBot("#bot-channel")

    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
                        datefmt='%Y-%d-%m %H:%M:%S', filename='server.log', level=logging.INFO)

    while True:
        try:
            rs.ring.update_dings()
            for alert in rs.ring.active_alerts():
                dev_id = str(alert['doorbot_id'])
                logging.info('Device: %s, Description: %s, Kind: %s',
                             alert['device_kind'] or '', alert['doorbot_description'] or '', alert['kind'] or '')
                if str(alert['kind']) == 'on_demand': # ding
                    rs.ring.update_devices()
                    bat_life = int(rs.get_battery_life(dev_id))
                    msg = "<!here> Someone is at the door!"
                    if bat_life <= 35:
                        msg = f"<!here> Someone is at the door! (battery: {bat_life}%)"
                    bot.send_message(msg)
                    rs.take_screenshot(dev_id)
                elif str(alert['kind']) == 'ding':
                    pass
            retries = 0 # reset so we have 5 more attempts after a successful run
        except:
            err = traceback.format_exc().replace('\n', '::')
            logging.warning("Problem during update_dings: " + err)
            retries += 1
            if retries >= max_retries:
                logging.error("Max retries hit - quitting")
                quit()
        sleep(loop_sleep)


if __name__ == "__main__":
    main()
