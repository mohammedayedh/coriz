from requests_tor import RequestsTor

enter_url=input("enter url onion: ")
requests=RequestsTor(tor_ports=(9050,), tor_cport=9051)
url =f"{enter_url}"
r=requests.get(url)

print(r.text)
