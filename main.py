import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from openai import OpenAI
import json

SBR_WS_CDP = 'wss://brd-customer-hl_ac20983b-zone-real_eastat_browser:p7uv889zr7qa@brd.superproxy.io:9222'
BASE_URL = "https://www.zoopla.co.uk/"
client = OpenAI(api_key='sk-proj-coVaMjrfuKtnikSfhMcJT3BlbkFJKdCVw0wvVqUq3gkD39ev')
LOCATION = "London"


def extract_picture(picture_section):
    picture_sources = []
    for picture in picture_section.find_all("picture"):
        for source in picture.find_all("source"):
            source_type = source.get("type", "").split('/')[-1]
            pic_url = source.get ("srcset", "").split(",")[0].split(" ")[0]

            if source_type == 'webp' and '1024' in pic_url:
                picture_sources.append(pic_url)
    return picture_sources

def extract_details(input):

    print("Extract Property...")
    command = """
            You are a data exractor mode and you have been tasked to extract information about apartment for me into a json file.
            Here is the div for the property details :
            {input_command}
            This is the final json structure expected :
            {{
            "price": "",
            "address":"",
            "bedrooms":"",
            "bathrooms":"",
            "receptions":"",
            "EPC Rating":"",
            "tenure":"",
            "time_remaining_on_lease":"",
            "service_charge":"",
            "countil_tax_band":"",
            "ground_rent":"",

            }}
    """.format(input_command=input)
    response =client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": command
            }
        ]
    )
    res = response.choices[0].message.content
    json_data =json.loads(res)
    return json_data

def extract_plan(soup):
    print("extract plan")
    plan = {}
    floor_plan = soup.find('div', {"data-testid":"floorplan-thumbnail-0"})
    if floor_plan :
        floor_plan_src = floor_plan.find("picture").find("source")["srcset"]
        plan["floor_plan"] = floor_plan_src.split(' ')[0]
    return plan

async def run(pw):
    print('Connecting to Scraping Browser...')
    browser = await pw.chromium.connect_over_cdp(SBR_WS_CDP)
    try:
        page = await browser.new_page()
        print(f'Connected! Navigating to {BASE_URL}')
        await page.goto(BASE_URL)
        await page.fill('input[name= "autosuggest-input"]', LOCATION)  # Corrected line
        await page.keyboard.press("Enter")

        print("Waiting ...")
        await page.wait_for_load_state("load")
        content = await page.inner_html('div[data-testid="regular-listings"]')
        # CAPTCHA handling: If you're expecting a CAPTCHA on the target page, use the following code snippet to check the status of Scraping Browser's automatic CAPTCHA solver
        # client = await page.context.new_cdp_session(page)
        # print('Waiting captcha to solve...')
        # solve_res = await client.send('Captcha.waitForSolve', {
        #     'detectTimeout': 10000,
        # })
        # print('Captcha solve status:', solve_res['status'])


        soup = BeautifulSoup(content, "html.parser")
        for idx, div in enumerate(soup.find_all("div",class_ = 'dkr2t82')):
            link = div.find('a')['href']
            data ={
                "adress" : div.find('address').text,
                "title" : div.find("h2").text,
                "link" : BASE_URL + link

            }
            print("Navigation to", link)
            await page.goto(data["link"])
            await page.wait_for_load_state("load")

            content = await page.inner_html("div[data-testid='listing-details-page']")
            soup = BeautifulSoup(content, "html.parser")
            picture_section = soup.find("section", {"aria-labelledby": "listing-gallery-heading"})
            pictures = extract_picture(picture_section)
            
            data['pictures'] = pictures

            property_details = soup.select_one('div[class="_14bi3x33z _14bi3x32f"]')
            #property_details = extract_details(property_details)
            floor_plan = extract_plan(soup)
            data.update(floor_plan)
            #data.update(property_details)
            print(data)
            break
        print('Navigated! Scraping page content...')
       # html = await page.content()
       # print(html)
    finally:
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':
    asyncio.run(main())

