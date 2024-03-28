from bs4 import BeautifulSoup
import requests
from data.db_session import global_init, create_session
from data.events import Events


def get_data_from_web_site():
    global_init("db/astronomy_site_users.db")
    session = create_session()
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


get_data_from_web_site()
