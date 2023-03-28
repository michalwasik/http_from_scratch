import requests

url_format = 'http://127.0.0.1:8888/{}'


def create_item(data: dict):
    response = requests.post(
        url_format.format(f'items'),
        json=data,
    )
    return response.status_code, response.content


def get_items():
    response = requests.get(
        url_format.format(f'items'),
    )
    return response.status_code, response.content


def get_item(item_id: int):
    response = requests.get(
        url_format.format(f'items/{item_id}'),
    )
    return response.status_code, response.content


def update_item(item_id: int, data: dict):
    response = requests.patch(
        url_format.format(f'items/{item_id}'),
        json=data,
    )
    return response.status_code, response.content


def delete_item(item_id: id):
    response = requests.delete(
        url_format.format(f'items/{item_id}'),
    )
    return response.status_code, response.content


def buy(item_id: int, data: dict):
    response = requests.post(
        url_format.format(f'items/{item_id}/buy'),
        json=data,
    )
    return response.status_code, response.content


def sleep(seconds: int):
    response = requests.get(url_format.format(f'sleep/{seconds}'))
    return response.status_code, response.content


# I recommend adding some code that will empty your database here
with open('database.json', 'w') as db:
    db.write('[]')

assert get_items() == (200, b'[]')
print(create_item({"name": "apple", "supply": 10, "price_per_item": 2.05, "available": True}))
assert (
    create_item({"name": "apple", "supply": 10, "price_per_item": 2.05, "available": True}) ==
    (201, b'{"name": "apple", "supply": 10, "price_per_item": 2.05, "available": true, "id": 1}')
)
# assert (
#     create_item({"name": "banana", "supply": 100, "price_per_item": 5.55, "available": True}) ==
#     (201, b'{"name": "banana", "supply": 100, "price_per_item": 5.55, "available": true, "id": 2}')
# )
# assert (
#     create_item({"name": "avocado", "supply": 23, "price_per_item": 15.99, "available": True}) ==
#     (201, b'{"name": "avocado", "supply": 23, "price_per_item": 15.99, "available": true, "id": 3}')
# )
# assert (
#     create_item({"name": "coconut", "supply": 45, "price_per_item": 1.00, "available": False}) ==
#     (201, b'{"name": "coconut", "supply": 45, "price_per_item": 1.0, "available": false, "id": 4}')
# )
# assert (
#     get_item(1) ==
#     (200, b'{"name": "apple", "supply": 10, "price_per_item": 2.05, "available": true, "id": 1}')
# )
# assert (
#     get_item(2) ==
#     (200, b'{"name": "banana", "supply": 100, "price_per_item": 5.55, "available": true, "id": 2}')
# )
# assert (
#     delete_item(2) ==
#     (200, b'{"name": "banana", "supply": 100, "price_per_item": 5.55, "available": true, "id": 2}')
# )
# assert (
#     update_item(2, {'name': 'I want to exist'}) ==
#     (404, b'{"detail": "Item with id 2 doesn\'t exist"}')
# )
# assert (
#     get_item(3) ==
#     (200, b'{"name": "avocado", "supply": 23, "price_per_item": 15.99, "available": true, "id": 3}')
# )
# assert (
#     get_item(4) ==
#     (200, b'{"name": "coconut", "supply": 45, "price_per_item": 1.0, "available": false, "id": 4}')
# )
# assert get_item(5) == (404, b'{"detail": "Item with id 5 doesn\'t exist"}')
# assert buy(1, {"amount": 10, "money": 1_000.00}) == (200, b'{"change": 979.5}')
# assert (
#     get_item(1) ==
#     (200, b'{"name": "apple", "supply": 0, "price_per_item": 2.05, "available": true, "id": 1}')
# )
# assert (
#     update_item(1, {"supply": 200, "price_per_item": 20.05}) ==
#     (200, b'{"name": "apple", "supply": 200, "price_per_item": 20.05, "available": true, "id": 1}')
# )
# assert buy(1, {"amount": 10, "money": 1_000.00}) == (200, b'{"change": 799.5}')
# assert (
#     get_item(1) ==
#     (200, b'{"name": "apple", "supply": 190, "price_per_item": 20.05, "available": true, "id": 1}')
# )
# assert (
#     create_item({"name": "grapes", "supply": 1, "price_per_item": 0.49, "available": True}) ==
#     (201, b'{"name": "grapes", "supply": 1, "price_per_item": 0.49, "available": true, "id": 5}')
# )
# assert (
#     get_item(5) ==
#     (200, b'{"name": "grapes", "supply": 1, "price_per_item": 0.49, "available": true, "id": 5}')
# )
# assert (
#     update_item(5, {"name": "not grapes", "supply": 0, "price_per_item": 0.61, "available": False}) ==
#     (200, b'{"name": "not grapes", "supply": 0, "price_per_item": 0.61, "available": false, "id": 5}')
# )
# assert (
#     get_item(5) ==
#     (200, b'{"name": "not grapes", "supply": 0, "price_per_item": 0.61, "available": false, "id": 5}')
# )
# assert (
#     update_item(5, {"name": "not grapes", "supply": 0, "gugu": "gaga", "available": False}) ==
#     (400, b'{"detail": "Too many fields: gugu"}')
# )
# assert (
#     update_item(5, {"name": "not grapes", "available": "not"}) ==
#     (400, b'{"detail": "Field available does not have proper type(type)"}')
# )
# assert(
#     get_items() ==
#     (
#         200,
#         b'[{"id": 1, "name": "apple"}, '
#         b'{"id": 3, "name": "avocado"}, '
#         b'{"id": 4, "name": "coconut"}, '
#         b'{"id": 5, "name": "not grapes"}]')
# )


# +++ Uncomment below to test threaded server +++

# sleep_times = [1, 2, 3, 2]
# IS_THREADED = True  # test for both True and False
#
# start = time.perf_counter()
# threads = [Thread(target=sleep, args=(sleep_time,)) for sleep_time in sleep_times]
# for thread in threads:
#     thread.start()
# for thread in threads:
#     thread.join()
# end = time.perf_counter()
# total = end - start
#
# if IS_THREADED:
#     print(f'threaded, waited for {total}')
#     assert abs(max(sleep_times) - total) < 0.1, sleep_times
# else:
#     print(f'non threaded, waited for {total}')
#     assert abs(sum(sleep_times) - total) < 0.1, sleep_times

print('SUCCESS')
