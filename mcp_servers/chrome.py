import asyncio
import logging  # Import the logging module

from pyppeteer import launch
from mcp.server.fastmcp import FastMCP

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mcp = FastMCP("A simple pyppeteer server for interacting with google chrome")

def take_screenshot(url: str, imagePath: str):

    async def main(url: str, imagePath: str):
        browser = await launch()

        try:
            page = await browser.newPage()
            await page.goto(url)
            await page.screenshot({"path": imagePath, "fullPage": True})
        except Exception as e:
            logging.warning(f"Hit exception while taking a screenshot of {url}: {e}")
        finally:
            await browser.close()

    asyncio.run(main(url, imagePath))

@mcp.tool()
def screenshot(url: str, imagePath: str) -> str:
    """
    Take a screenshot of a webpage and save it to imagePath

    Args:
        url: Fully formed URL
        imagePath: Path where resulting PNG image should be stored
    Returns:
        imagePath
    """
    take_screenshot(url, imagePath)
    return imagePath

def main():
    logging.info("Starting pyppeteer server")
    mcp.run()

if __name__ == "__main__":
    take_screenshot("https://www.hackernews.com", "/tmp/a.png")
