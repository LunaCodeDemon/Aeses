#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from bot import client

client.run(os.environ.get('DISCORD_TOKEN'))
