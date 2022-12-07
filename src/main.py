#!/usr/bin/env python3
import os
import sys

import app


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    app = app.TuxMenu()
    app.main()
