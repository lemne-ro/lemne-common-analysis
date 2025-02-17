import threading
from config import get as get_config
from base_worker import BaseWorker


# configz
config = get_config()

# main
if __name__ == '__main__':
    test = BaseWorker(config)
    thread = threading.Thread(target=test.run)
    thread.start()

