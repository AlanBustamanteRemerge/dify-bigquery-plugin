#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dify_plugin import register_tool, register_provider

# Register provider
from provider.bigquery import provider as bigquery_provider
register_provider(bigquery_provider)

# Register tools
from tools.bigquery_query import tool as bigquery_query_tool
register_tool(bigquery_query_tool) 