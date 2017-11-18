#!/usr/bin/python3

import os
import re
for f in os.listdir('.'): os.rename(f, re.sub(r'[^a-zA-Z0-9\.]', '', f))
