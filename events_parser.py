from bs4 import BeautifulSoup
import requests
from data.data_base_session import data_base_init, new_session
from data.events import Events


def get_data_from_web_site():
    data_base_init("dbs/astronomy_site_users.db")
    session = new_session()
    url = "https://starwalk.space/ru/news/astronomy-calendar-2024"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    events_dict = {}
    for event in soup.find("ul", class_="toc"):
        text = event.text.split("\n\n")
        events = "".join(text[1:]).split("\n")
        if events[0] != '':
            events_dict[text[0]] = events
    for key, value in events_dict.items():
        main_event = Events()
        main_event.date_of_event = key
        main_event.events = ", ".join(list(map(lambda event: event.title(), value)))
        session.add(main_event)
        session.commit()

