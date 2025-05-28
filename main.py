#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Add the parent directory to the Python path to allow for absolute imports.
#, e.g. fromหลวงพ่อ tool_excel.tools.excel_tool import ExcelTool
# If you plan to use this in your own project, you may want to remove this if you have a different way of handling imports.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(APP_ROOT, ".."))

# Import provider and tool modules to allow them to be discovered.
import minimal_provider # Adjusted import path
import minimal_tool       # Adjusted import path

# from dify_plugin.runner import application # This is for newer SDK versions (like 0.3.x)
from dify_plugin.runner import application

# Add your tool and provider to the application
# No explicit registration needed if classes inherit from Tool/ToolProvider correctly

if __name__ == "__main__":
    # This will start a http server and wait for requests.
    # The Dify plugin daemon will send requests to this server.
    application.run()

# The Dify plugin daemon should automatically discover and register
# the provider and tool if they are correctly defined and inherit
# from dify_plugin.ToolProvider and dify_plugin.Tool respectively. 