
import requests

"""Login qilib token olish"""
url = f"https://api.venu.uz/seller/auth/login"

API_KEY = "XOjOXviWzeiEBdeULDZYRfCKdDk6fMNPjSgKhjLZ"

headers = {
    "accept-encoding": "gzip",
    "content-type": "application/json; charset=UTF-8",
    "authorization": f"Bearer {API_KEY}",
    "user-agent": "Python/requests"
}

# Venu
# EMAIL = "themodestn@venu.uz"
# PASSWORD = "Themodestn@venu3001.uz"

# Antique
EMAIL = "testdokon@antik.uz"
PASSWORD = "Testdokon@antik.uz2026"

data = {
    "email": EMAIL,
    "password": PASSWORD
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(response.status_code)
 
# url = "https://api.venu.uz/vendor/products/status-update"
#
# headers = {
#     "Accept": "*/*",
#     "Accept-Language": "en-US,en;q=0.9,uz;q=0.8,ru;q=0.7",
#     "Connection": "keep-alive",
#     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#     "Origin": "https://api.venu.uz",
#     "Referer": "https://api.venu.uz/vendor/products/list/all",
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
#     "X-CSRF-TOKEN": "nmFc8gq2uMrZhe6XjhQNIo7CJcnJLGcwSWJ2jalc",
#     "X-Requested-With": "XMLHttpRequest",
#     "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Linux"',
# }
#
# cookies = {
#     "AMP_MKTG_465aeba67e": "JTdCJTdE",
#     "remember_seller_59ba36addc2b2f9401580f014c7f58ea4e30989d": "eyJpdiI6IlllVjFtT3Z1aERWYTNBSEFqcFpnWXc9PSIsInZhbHVlIjoiZ2Y1M3FrR2tDOW4ycmVObDNiTE1XRHcvUjJCOC9jWHFYQTlUWFpwUDlwd2E3NURNd2NqVkxxc3BRK0tIMjRUV2NtSElkZDBVN1RFRElySTZiajloS0ZEeUMwejVmQjBBVWhaQVorWVZZbmV1b3V6ZXJBRDZrcStuQlArb0RUQmMrWWI0amhTQ2FZZTloL0VrVDNFRStyWWhaSW1CZE9RL0ZqSURwMEJRZUlHYnBNclpqaFkvVzNSeXdTM2c5WndpQTh3K1psa25yWVRzclRGcXVwVmFLcXcwaU5KNmsycTV6cUlTbkl1UDkrbz0iLCJtYWMiOiIwZGZjYzExZGM2NTcxOWU1YmY2MDE1OTM5ZjczZGIzNzdlZjAzZTM2YjkxMmYzYWE3ZjA1MTc5Y2ZhZDQ1MWM2IiwidGFnIjoiIn0=",
#     "XSRF-TOKEN": "eyJpdiI6IkxxUUNKQ1BlZlBQZGRPK1BLRmh4d0E9PSIsInZhbHVlIjoiOGU0Uzl4NDZhQW9Hc3hhQjg0VTFZV1dCRThDQWVUNWN0TU8rN3k4TmVzNXFsaGxEQ3FYUXowa3lnMHV0TzdQR2pLZEVzanNKYW9qcVM4a1JxUTh4Rk41OFgwRE5PcGdyQTZUQVkreU9kRS9acmxQRERnLzRMZ0pLa3VlSzdSTmEiLCJtYWMiOiJiZmE4ZDFmMWE3MThkZTBkMjQ1ZmFhMDExZmZiY2E4ZDk3MGUwMzk0MjRlNzkyZjNiMjBmMGM4ZGZjYjJmODQ1IiwidGFnIjoiIn0=",
# }
#
# data = {
#     # "_token": "nmFc8gq2uMrZhe6XjhQNIo7CJcnJLGcwSWJ2jalc",
#     "id": 13388,
#     "status": 1
# }
#
# response = requests.post(
#     url,
#     headers=headers,
#     cookies=cookies,
#     data=data
# )
#
# print("Status code:", response.status_code)
# print("Response:", response.text)
