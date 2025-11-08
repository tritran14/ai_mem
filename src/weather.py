#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 08, 2025 16:43:27$"

from typing import Any
import httpx
import logging
import time
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_traffic.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    start_time = time.time()
    logger.info(f"[TRAFFIC] Tool called: get_alerts | Parameters: state={state}")
    
    try:
        url = f"{NWS_API_BASE}/alerts/active/area/{state}"
        data = await make_nws_request(url)

        if not data or "features" not in data:
            result = "Unable to fetch alerts or no alerts found."
            logger.warning(f"[TRAFFIC] get_alerts failed | state={state} | duration={time.time()-start_time:.2f}s")
            return result

        if not data["features"]:
            result = "No active alerts for this state."
            logger.info(f"[TRAFFIC] get_alerts success (no alerts) | state={state} | duration={time.time()-start_time:.2f}s")
            return result

        alerts = [format_alert(feature) for feature in data["features"]]
        result = "\n---\n".join(alerts)
        logger.info(f"[TRAFFIC] get_alerts success | state={state} | alerts_count={len(alerts)} | duration={time.time()-start_time:.2f}s")
        return result
    except Exception as e:
        logger.error(f"[TRAFFIC] get_alerts error | state={state} | error={str(e)} | duration={time.time()-start_time:.2f}s")
        raise


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    start_time = time.time()
    logger.info(f"[TRAFFIC] Tool called: get_forecast | Parameters: latitude={latitude}, longitude={longitude}")
    
    try:
        # First get the forecast grid endpoint
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await make_nws_request(points_url)

        if not points_data:
            result = "Unable to fetch forecast data for this location."
            logger.warning(f"[TRAFFIC] get_forecast failed | lat={latitude}, lon={longitude} | duration={time.time()-start_time:.2f}s")
            return result

        # Get the forecast URL from the points response
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_request(forecast_url)

        if not forecast_data:
            result = "Unable to fetch detailed forecast."
            logger.warning(f"[TRAFFIC] get_forecast failed (no forecast) | lat={latitude}, lon={longitude} | duration={time.time()-start_time:.2f}s")
            return result

        # Format the periods into a readable forecast
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
            forecasts.append(forecast)

        logger.info(f"[TRAFFIC] get_forecast success | lat={latitude}, lon={longitude} | periods={len(periods)} | duration={time.time()-start_time:.2f}s")
        return "\n---\n".join(forecasts)
    except Exception as e:
        logger.error(f"[TRAFFIC] get_forecast error | lat={latitude}, lon={longitude} | error={str(e)} | duration={time.time()-start_time:.2f}s")
        raise


def main():
    # Initialize and run the server
    logger.info("[TRAFFIC] MCP Weather Server starting...")
    logger.info(f"[TRAFFIC] Logging traffic to: mcp_traffic.log")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
