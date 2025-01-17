import requests
import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8') # ensures correct encoding or python freaks out

def clear():
    os.system("cls")

def getFriends(userId):
    friends = []
    url = f"https://friends.roblox.com/v1/users/{userId}/friends/find"

    cursor = None
    params = {'cursor': cursor} 
    while True:
        params = {"Cursor" : cursor}
        response = requests.get(url, params = params) # gets friend page, limited to 50 per page
        data = response.json()
        friends.extend(data["PageItems"])
        cursor = data.get('NextCursor')
        if cursor: # checks to see if next cursor exists
            continue
        break
    return friends

def diffFriends(friends1, friends2): # finds which ids are newly added
    removeFriends = []

    for i in range(len(friends2)):
        if friends2[i] not in friends1:
            removeFriends.append(friends2[i])

    return removeFriends

def retrieveCSRF(cookie): # gets the refreshed CSRF token to unadd friends
    url =  "https://auth.roblox.com/v2/logout"
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}"
    }
    try:
        data = requests.post(url, headers = headers)
        csrfToken = data.headers['x-csrf-token']
    except:
        return False
    return csrfToken

def getUsername(robloxId, nameType): # True is username, False is displayname
    data = requests.get(f"https://users.roblox.com/v1/users/{robloxId}").json()
    if nameType:
        return data['name']
    else:
        return data["displayName"]

def friendCheck(friendList): # generates names of removed friends
    names = ""
    len = -1
    for i in friendList:
        len += 1
        id = i["id"]
        names += f"{len}. Username: {getUsername(id, True)} | Display Name: {getUsername(id, False)}\n"     
    clear()
    print(names)
    return friendList

def removeFriends(friendList):
    with open('cookie.txt', 'r') as file: 
        cookie = file.read().strip()

    while True:
        friendList = friendCheck(friendList)
        try:
            choice = int(input("If you would like to keep someone from getting removed, just enter the number at the start of their line (1 person at a time)\nEnter anything else if you'd like to continue to remove EVERYONE seen above\n"))
        except:
            break
        if choice < len(friendList):
            friendList.pop(choice)
            clear()
            print("Loading...")

    while True:
        clear()
        print("Loading...")
        friendCheck(friendList)
        choice = input("If you're happy to remove all of these people, enter 'Y', else close the program now.\n").lower()
        if choice == "y":
            break

    while len(friendList) != 0:
        userId = friendList[0]["id"]
        url = f"https://friends.roblox.com/v1/users/{userId}/unfriend"
        headers = {
            "Cookie": f".ROBLOSECURITY={cookie}",
            "X-CSRF-TOKEN": retrieveCSRF(cookie)
        }
        data = requests.post(url, headers = headers)
        print(f"Removed {getUsername(userId, False)}")
        friendList.pop(0)
    print("Closing in 5...")
    time.sleep(5)

def autoRemover(friends1, id): # gets friends list before and after and removes newly added friends
    while True:
        wait = input("If you are now ready to remove your newly added friends, press and enter the key (Y) to continue!\n(no one will be removed yet, will need confirmation on the names to remove at a later step)\n").lower()
        if wait == "y":
            clear()
            print("Loading...")
            break
        clear()

    friends2 = getFriends(id)

    diff = diffFriends(friends1, friends2)
    removeFriends(diff)

def friendChecker(friends1, id):
    while True:
        wait = input("If you are now ready to recieve the list of users to remove, press and enter the key (Y) to continue!\n").lower()
        if wait == "y":
            clear()
            print("Loading...")
            break
        clear()
    
    friends2 = getFriends(id)

    diff = diffFriends(friends1, friends2)
    names = "Remove List:\n"
    for i in diff:
        id = i["id"]
        names += f"Username: {getUsername(id, True)} | Display Name: {getUsername(id, False)}\n"    
    clear()
    print(names) 
    input("Press anything to close the program\n")

def options(allow, id):
    print("Loading Current Friends List...")
    friends1 = getFriends(id)
    clear()
    while True:
        print(f"Welcome to my auto unfriending tool, {getUsername(id, False)}!\nThis tool was mainly made for ACB by @mmiikkeeyy (Owner of the best guild?)\nPlease select an option below that matches your preference:")

        choice = input("1. Auto Remove Friends (Requies a valid cookie within cookie.txt file)\n2. Tells you the username of all the newly added friends (Requires your Roblox Name)\nPlease enter in the number for your choice: ")
        if choice == "1" and allow:
            clear()
            autoRemover(friends1, id)
            break
        elif choice == "2":
            clear()
            friendChecker(friends1, id)
            break
        elif choice == "1" and not allow:
            print("Cannot select this option as you have an invalid cookie in the cookie.txt file, please retry the steps with a valid cookie")
            time.sleep(3)
            clear()

def main():
    try:
        with open('cookie.txt', 'r') as file: # gets da cookie from the file
            cookie = file.read().strip()
    except:
        cookie = None

    value = retrieveCSRF(cookie)

    if value: # auto grabs users id for tracking friends
        url = "https://users.roblox.com/v1/users/authenticated"
        headers = {
            "Cookie": f".ROBLOSECURITY={cookie}"
        }
        id = requests.get(url, headers=headers).json()
        options(True, id['id'])

    else:
        while True:
            nameToId = input("Hey! Either you don't have a cookie in cookie.txt or an invalid one, if you want to see a list of the people you need to remove instead of automatic removal please type your roblox username: ")
            try:
                url = "https://users.roblox.com/v1/usernames/users"
                id = requests.post(url, json = {"usernames" : [nameToId]}).json()
                id = id['data'][0]['id']
            except:
                print("Didn't work, try entering your name again")
                time.sleep(2)
                clear()
                continue
            break

        options(False, id)

main()
