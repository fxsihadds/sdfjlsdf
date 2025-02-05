import requests
import json
import time


class Scrapper:
    def __init__(self, data) -> None:
        self.url = "https://api.subsource.net/api/searchMovieFull"
        self.data = {"query": data}
        self.keyword = data
        self.session = requests.Session()

    def _x__request(self):
        headers = {
            "Host": "api.subsource.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Origin": "https://subsource.net",
            "Connection": "keep-alive",
            "Referer": "https://subsource.net/",
        }
        try:
            rq = self.session.post(self.url, headers=headers, json=self.data, timeout=5)
            data = rq.json()
            found = data.get("found", [])
            if found:
                movie = {}
                for item in found:
                    title = item.get("title")
                    poster = item.get("poster")
                    if title not in movie:
                        movie[title] = []
                    for seasons in item.get("seasons", []):
                        number = seasons.get("number")
                        full_link = seasons.get("fullLink")
                        season_data = {
                            "Season": number,
                            "Full Link": "https://subsource.net" + full_link,
                            "Poster": poster,
                        }
                        movie[title].append(season_data)

                index = 1
                for movie_title, seasons in movie.items():
                    for season in seasons:
                        season_number = season["Season"]
                        print(f"Index {index}: {movie_title} - Season {season_number}")
                        print("-" * 30)
                        index += 1

                while True:
                    try:
                        user_inp = int(input("Please choose a movie by index: "))
                        if 1 <= user_inp < index:
                            break
                        else:
                            print("Please enter a valid index.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

                selected_index = 1
                for movie_title, seasons in movie.items():
                    for season in seasons:
                        if selected_index == user_inp:
                            return self._download_request(season["Full Link"])
                        selected_index += 1
            else:
                print("NOT FOUND")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _download_request(self, link):
        print(link)
        headers = {
            "Host": "api.subsource.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Origin": "https://subsource.net",
            "Connection": "keep-alive",
            "Referer": "https://subsource.net/",
        }
        part = link.split("/")
        print(part)
        payload = {
            "langs": "",
            "movieName": f"{part[4]}",
            "season": f"{part[5]}",
        }

        rq = self.session.post(
            "https://api.subsource.net/api/getMovie",
            json=payload,
            headers=headers,
            timeout=5,
        )

        # print(rq.json())
        # with open('movies.json', mode='a+', encoding='utf-8') as data:
        # data.write(str(rq.text))
        found = rq.json()
        for item in found.get("subs", []):
            if item.get("lang") == "Bengali":
                link = item.get("fullLink")
                load = {
                    "movie": f"{item.get('linkName')}",
                    "lang": "Bengali",
                    "id": f"{link.split('/')[4]}",
                }
                print(load)
                # print(link)
                # time.sleep(3)
                down = self.session.post(
                    "https://api.subsource.net/api/getSub",
                    json=load,
                    headers=headers,
                    timeout=5,
                )
                download = down.json()
                # print(download)
                if download.get("sub") and download["sub"].get("downloadToken"):
                    download_link = f'https://api.subsource.net/api/downloadSub/{download["sub"]["downloadToken"]}'
                    response = self.session.get(download_link, stream=True)
                    file_name = f"{download['sub'].get('ri')[0]}.zip"
                    with open(file_name, mode='wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            print(f"Downloaded: {file_name}")
                else:
                    print("NOT FOUND!")

            else:
                print("NOT FOUND!")


"""rq1 = Scrapper("Tale of the Nine Tailed")
rq1._x__request()"""
