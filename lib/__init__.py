import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(filename)s:%(lineno)d: %(message)s')

# Quiet down logging from the requests module
logging.getLogger('requests').setLevel(logging.WARN)

# We want our own logs at INFO level
log = logging.getLogger('thresholderbot')
log.setLevel(logging.INFO)
