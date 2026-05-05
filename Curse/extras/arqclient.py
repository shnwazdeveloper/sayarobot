import os

from Python_ARQ import ARQ

from Curse.extras.https import session

ARQ_API_KEY = os.environ.get("ARQ_API_KEY", "")
ARQ_API_URL = os.environ.get("ARQ_API_URL", "arq.hamker.dev")

arq = ARQ(ARQ_API_URL, ARQ_API_KEY, session)
