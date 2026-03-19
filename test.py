# test_submit.py  — run with: python test_submit.py
import requests

code = """def find_all_duplicates(input_list):
    seen = set()
    duplicates = set()
    for item in input_list:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

my_list = [1, 2, 3, 1, 2, 5]
print(find_all_duplicates(my_list))
"""

r = requests.post("http://127.0.0.1:8000/api/submit", json={
    "session_id": "1",
    "code": code,
    "language": "python"
})
print(r.status_code)
print(r.json())