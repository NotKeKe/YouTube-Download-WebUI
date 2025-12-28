import requests

resp = requests.post('http://localhost:8127/download', json={'url': 'https://music.youtube.com/watch?v=9LjMkHFnlUU&si=gKwL-sLjriNdAmMl', 'type': 'audio'})

print(resp.status_code)
print(resp.headers)
# print(resp.text)