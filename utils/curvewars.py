from requests import post, get 
from json import dumps as jsondumps

CURVEWARSDOMAIN = "https://curvewars.com"
CURVEWARSAPI = CURVEWARSDOMAIN + "/api"

class NoCredentials(Exception):
    pass   

class CurveWarsWrapper:

    def __init__(self, *args, username = None, password = None, **kwargs):
        self.username = username
        self.password = password

    def CheckCredentials(func):
        def wrapper(self):
            if not self.username:
                raise NoCredentials("bad username")

            if not self.password:
                raise NoCredentials("bad password")

            func(self) 

        return wrapper 

    @CheckCredentials
    def authenticate(self):
        loginPage = post(CURVEWARSAPI + "/auth/login", json={"username": self.username, "password": self.password})
        response = loginPage.json()
        cookie = {"cwtoken": response["token"]}
        header = {"Authorization": "Bearer "+response["token"], "Cookie": "cwtoken="+response["token"]}
        return (cookie, header)

    @property
    def BasicProfile(self):
        token = self.authenticate()
        request = post("https://curvewars.com/api/stat", json={"username": self.username}, cookies=token[0], headers=token[1])
        try:
            response = request.json()
            print(response)
            for i in response[0]["stat"]:
                if self.username in i["player"].values():
                    userLoc = i["player"]
            results = {
                "id": userLoc["id"],
                "username": userLoc["username"],
                "country": userLoc["country"],
                "email": userLoc["email"],
                "playerStates": {
                    "isAdmin": userLoc["isAdmin"],
                    "isMod": userLoc["isModerator"],
                    "isChamp": userLoc["isChamp"],
                    "premiumLevel": userLoc["premiumLvl"]
                    },
                "balances": {
                    "coins": userLoc["coins"],
                    "diamonds": userLoc["diamonds"],
                    "gPoints": userLoc["gPoints"]
                    },
                "preferences": {    
                    "controls": {"leftKey": userLoc["leftKey"], "rightKey": userLoc["rightKey"]},
                    "keylag": userLoc["keylag"],
                    "icon": userLoc["icon"],
                    "clantag": userLoc["clantag"],
                    "favColor": userLoc["preferedColor"],
                    },
                "FFA": {
                    "totalGames": userLoc["ffaPlays"],
                    "gamesWon": userLoc["ffaWins"],
                    "rank": userLoc["ffaRank"],
                    },
                "Team": {
                    "totalGames": userLoc["teamPlays"],
                    "gamesWon": userLoc["teamWins"],
                    "rank": userLoc["teamRank"],
                    },
                "1v1": {
                    "totalGames": userLoc["ovoPlays"],
                    "gamesWon": userLoc["ovoWins"],
                    "rank": userLoc["ovoRank"],
                    },
                }
            return jsondumps(results)
        except Exception as e:
            return e

    @property
    def ActiveRooms(self):
        results = {}
        request = get(CURVEWARSDOMAIN + "/matchmake/")
        response = request.json()
        def gameType(string):
            return {'ffa':'FFA','two':'Two Teams','three':'Three Teams'}[string]
        for idx, val in enumerate(response):
            if val["name"] == "main" and val["maxClients"] == 500: continue
            gameLoc = val["metadata"]
            def getPlayers():
                players = gameLoc["players"]
                if gameLoc["game_type"] == "ffa":
                    return {p["username"]: p for p in players}
                else:
                    teams = [[], [], []]
                    for x in players:
                        teams[x["team"]].append(x)
                    teamsD = {"teamOne": teams[0], "teamTwo": teams[1], "teamThree": teams[2]}
                    return {k: {p["username"]: p for p in v} for k, v in teamsD.items()}
            teamScores = gameLoc["teamWinners"]
            results[idx] = {
                    "Room Name": gameLoc["name"],
                    "Player Count": gameLoc["players_in"],
                    "Average Rank": gameLoc.get("avg_rank", 0),
                    "Game Started": gameLoc["game_started"],
                    "Settings": {
                        "Gamemode": gameType(gameLoc["game_type"]),
                        "Ranked": gameLoc["ranked"],
                        "Total Players": gameLoc["players_count"],
                        "Drop Probability": gameLoc["drop_probability"],
                        "Map Size": gameLoc["room_size"],
                        "Powerups": gameLoc["powerups"],
                        },
                    "Players": getPlayers(),
                    "RoomID": val["roomId"],
                    "Team Score": {
                        "teamOne": teamScores["0"],
                        "teamTwo": teamScores["1"],
                        "teamThree": teamScores["2"],
                    },
                }
        return jsondumps(results)

    @property
    def GameMedia(self):
        icons = {}
        powerups = {}
        colors = {}
        media = {}
        request = get(CURVEWARSAPI + "/media/")
        response = request.json()
        for i in response["icons"]:
            def coinVal():
                if "coins" in i:
                    return i["coins"]
                else:
                    return "0"
            icons[int(i["id"])] = {
                "name": i["name"],
                "coins": coinVal(),
                "file": i["icon"],
                "desc": i["description"],
                }
        for i in response["colors"]:
            colors[int(i["id"])] = {
                "name": i["name"],
                "coins": i["costs"],
                "file": i["texture"],
                "pattern": i["pattern"],
                "contains": i["colors"],
                }
        for i in response["powerups"]:
            powerups[int(i["id"])] = {
                "file": i["icon"],
                }
        media = {"icons": icons, "colors": colors, "powerups": powerups}
        return jsondumps(media)


# def MatchResults(matchid):
#     pass