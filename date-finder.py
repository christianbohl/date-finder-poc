from typing import Any
from mcp.server.fastmcp import FastMCP
import pandas as pd
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv() 

# Initialize FastMCP server
mcp = FastMCP("Date-Finder")

DATE_FINDER_API_KEY = os.getenv('DATE_FINDER_API_KEY')

@mcp.tool()
async def date_match(query: str) -> str:
    """
    Perfoms an HTTPS request with a query regarding characteristics for a potential date.
    The profiles that best match the query are returned.

    Args:
        query: String containing characteristics of potential date. 
    """
    try:
        # DEFINE API KEY  for https request on GCP server
        headers = {"X-API-KEY": DATE_FINDER_API_KEY}

        # POST request to the GCP server with API KEY and query for dating profile
        response = requests.post(
            "https://dates-finder-1005068255955.europe-west2.run.app/date-search",
            headers = headers,
            json = {"user_input":query})  # JSON payload

        #get the response and store it
        data = response.json()

        with open("response.json", "w") as json_file:
            json.dump(data, json_file, indent = 4)

        # get profile values
        profile = data.get("response",False).get("Match_0",False)

        #return values if exists
        if profile:
            return f"The following profile was returned based on your description:\n {profile}"
        else:
            return f"The API call found the following error: {data.get("error")}"

    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')