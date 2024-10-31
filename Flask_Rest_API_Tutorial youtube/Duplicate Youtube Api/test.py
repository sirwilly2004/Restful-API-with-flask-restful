import requests


BASE = "http://127.0.0.1:5000/"



# input()
response = requests.get(BASE + 'video/2')
print(response.json())


# response = requests.patch(BASE + 'video/1', {'views':5000})
# print(response.json())