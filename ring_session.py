import json
import getpass
import logging
from uuid import uuid4 as uuid
from ring_doorbell import Ring, Auth
from pathlib import Path


class RingSession:
    """
    Starts a Ring session. Create a cache file and pass it into this class. On first run, use your user/password/token (I verified from the app)
    to log in. Once you have a token, you will re-use the token from the cache file to establish new sessions.
    """

    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.ring = None
        logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
                        datefmt='%Y-%d-%m %H:%M:%S', filename='server.log', level=logging.INFO)

    def get_doorbot_by_id(self, id: str):
        if self.ring == None:
            return
        devices = self.ring.devices()
        for device in devices['doorbots'] or []:
            if str(device.id) == id:
                return device
        return None

    def take_screenshot(self, device_id: str):
        if self.ring == None:
            return
        device = self.get_doorbot_by_id(device_id)
        if device != None:
            device.get_snapshot(retries=3, delay=2, filename="last_screenshot.jpg")
    
    def get_battery_life(self, device_id: str):
        if self.ring == None:
            return None
        device = self.get_doorbot_by_id(device_id)
        if device != None:
            return device.battery_life
        return None
    
    def hardware_id(self, hwp) -> str:
        if hwp.is_file():
            return str(hwp.read_text())
        else:
            uid = str(uuid())
            hwp.write_text(uid)
            return uid

    def token_updater(self, token):
        """Write to the cache file to update with the latest refresh token. Used by the Auth class"""
        token['scope'] = "client" # I overwrote this because other API's use "client" instead of ["client"]
        self.cache_file.write_text(json.dumps(token))

    def create_ring(self):
        """Authenticates your user and returns a Ring instance to be queried further."""
        if self.cache_file.is_file():
            auth = Auth("android:com.ringapp",
                        json.loads(self.cache_file.read_text()), self.token_updater, self.hardware_id(Path('hw_id.cache')))
        else:
            username = input("user: ")
            password = getpass.getpass("password: ")
            token = input("2FA code: ")
            auth = Auth("android:com.ringapp", None, self.token_updater, self.hardware_id(Path('hw_id.cache')))
            try:
                auth.fetch_token(username, password, token)
            except:
                logging.error("Problem fetching token from input authorization.")
                quit()

        ring = Ring(auth)
        if ring.session is None:
            try:
                ring.create_session()
            except:
                logging.error("Authorization error - token likely expired.")
                quit()
        self.ring = ring
