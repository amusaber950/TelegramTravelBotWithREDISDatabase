import json
import requests
from datetime import date, datetime, timedelta
from typing import Any

LOCALE = 'en_US'
CURRENCY = 'USD'
URL = "https://hotels4.p.rapidapi.com/locations/v2/search"
HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': "e161630d38msh46ef8e8a5aa3f7ep184e7fjsn0a81f1e82b70"
}

n = 0


def api_request(querystring: Any, url: Any, headers: dict[str, str] = HEADERS) -> Any:
    """
    Function receives type of request and url
    :param1 querystring: querystring
    :param2 url: url
    :param headers: headers
    :return: dictionary
    """
    api_response = requests.request("GET", url, headers=headers, params=querystring)
    api_response = json.loads(api_response.text)
    return api_response


def get_destination_id(city: Any, locale: str = LOCALE, currency: str = CURRENCY,
                       *args: Any, **kwargs: Any) -> Any | None:
    """
    Finding and passing forward town
    code, if town is not presented
    in the web page data,
    returns message of mistake
    :param1 city: city name
    :param2 locale: type of language in use
    :param3 currency: type of currency
    :return: str
    """
    res = str(city)
    town = " "
    if "-" in res:
        town = (" ".join(res.split("-"))).lower()
    else:
        town = res.lower()
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": town, "locale": locale, "currency": currency}
    if city:
        response = api_request(querystring, url)
        try:
            destination_id = response['suggestions'][0]['entities'][0]['destinationId']
        except IndexError as error:
            destination_id = None
        return destination_id
    else:
        print('city is empty')


def get_properties_list(destination_id: Any, locale: str = LOCALE, currency: str = CURRENCY) -> Any:
    """
    Finding and passing forward information
    about hotels in the city
    :param1 destination_id: destination id
    :param2 locale: type of language in use
    :param3 currency: type of currency
    :return: dictionary
    """
    today = date.today()
    next_day = str(today + timedelta(days=5))
    try:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": str(today),
                       "checkOut": str(next_day), "adults1": "1", "sortOrder": "PRICE", "locale": locale,
                       "currency": currency}
        response = api_request(querystring, url)
        response = response['data']['body']['searchResults']['results']
    except AttributeError:
        raise Exception
    return response


def get_hotel_photos(hotel_id: Any) -> Any:
    """
    Finding and passing forward dict with photographs of hotel
    :param1 hotel_id: hotel id
    :return: dictionary
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}
    response = api_request(querystring, url)
    return response


def get_hotels(command: Any, city: Any, res_number: Any, img_num: Any):
    """
    Function for two commands - highprice, lowprice,
    uses three functions
    get_destination_id,
    get_properties_list
    get_hotel_photos,
    returns final list of data
    :param1 command: command
    :param2 city: city
    :param3 res_number: res_number
    :param4 img_num: img_num
    :return: list
    """

    api_response = []
    destination = get_destination_id(city)
    hotels = get_properties_list(destination)
    if command == "/lowprice":
        hotels = hotels[:int(res_number)]
    elif command == "/highprice":
        num = len(hotels) - int(res_number)
        hotels = hotels[num:]
    for hotel in hotels:
        response = {'hotel_name': hotel['name'], 'hotel_rating': hotel['starRating'],
                    "address": hotel["address"].get('streetAddress'),
                    "price": hotel['ratePlan'].get('price').get('exactCurrent'),
                    'distance': hotel['landmarks'][0].get('distance')}
        images = get_hotel_photos(hotel['id'])
        hotel_images = []
        for image in images['hotelImages']:
            hotel_images.append(image['baseUrl'].replace('{size}', 'z'))
        response['hotel_images'] = hotel_images[: int(img_num)]
        api_response.append(response)
    return api_response


def get_hotels2(dest: Any, res_number: Any, price: Any,
                distance: Any, visit_time: Any, img_num: Any):
    """
    Function for command - bestdeal,
    uses three functions
    get_destination_id,
    get_properties_list
    get_hotel_photos,
    returns final list of data
    :param1 dest: dest
    :param2 res_number: res_number
    :param3 price: price
    :param4 distance: distance
    :param5 visit_time: visit_time
    :param6 img_num: img_num
    :return: list
    """
    destination = get_destination_id(dest)
    hotels = get_properties_list(destination)
    api_response = []
    for hotel in hotels:
        h_dist = hotel['landmarks'][0].get('distance')
        h_price = hotel['ratePlan'].get('price').get('exactCurrent')
        if float(h_dist.rstrip(" miles")) <= float(distance) and float(h_price) <= float(price):
            response = {'hotel_name': hotel['name'], 'hotel_rating': hotel['starRating'],
                        "address": hotel["address"].get('streetAddress'),
                        "price": h_price,
                        "total_price": round(float(h_price), 2) * float(visit_time),
                        'distance': h_dist}
            images = get_hotel_photos(hotel['id'])
            hotel_images = []
            for image in images['hotelImages']:
                hotel_images.append(image['baseUrl'].replace('{size}', 'z'))
            response['hotel_images'] = hotel_images[:int(img_num)]
            api_response.append(response)

        else:
            print('No answer')
    return api_response[:int(res_number)]


def deal_with_none(lst):
    """Function swaps None-s with empty string
    :return: list
    """
    for el in lst:
        for key, val in el.items():
            if val is None:
                el[key] = ''
    return lst


def date_count(check_entry: Any, check_exit: Any) -> int:
    """Function counting difference between two dates
    :return: integer
    """
    date_format = '%d.%m.%Y'
    a = datetime.strptime(check_entry, date_format)
    b = datetime.strptime(check_exit, date_format)
    stay = b - a
    return stay.days
