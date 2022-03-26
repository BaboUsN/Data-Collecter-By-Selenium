from base64 import encode
from cmath import exp
import datetime
import json
from webbrowser import get
from bs4 import BeautifulSoup
import pytz
from selenium import webdriver
import time
import User

browser = webdriver.Chrome()
errorCounter = 0


def noLoopControler():
    global errorCounter
    if errorCounter >= 3:
        noLoopVarFormater()
        return True
    else:
        errorCounter += 1
        return False


def noLoopVarFormater():
    errorCounter = 0


def loginSkipButtonFun():
    try:
        loginSkipButton = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/div/div/div/button")
        loginSkipButton.click()
        time.sleep(2)
        loginSkipButton2 = browser.find_element_by_xpath(
            "/html/body/div[5]/div/div/div/div[3]/button[2]")
        loginSkipButton2.click()
        time.sleep(2)
    except Exception:
        if(noLoopControler()):
            return
        print("Hata olustu", "       ", Exception)
        print("1 saniye sonra tekrar denenecek")
        time.sleep(1)
        loginSkipButtonFun()
    noLoopVarFormater()


def loginTryer():
    try:
        browser.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)
        namePlace = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[1]/div/label/input")
        passwordPlace = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[2]/div/label/input")

        namePlace.send_keys(User.USER_NAME)
        passwordPlace.send_keys(User.USER_PASSWORD)
        time.sleep(1)
        loginButton = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[3]/button/div")
        loginButton.click()
        time.sleep(3)
    except Exception:
        print("Hata olustu", "       ", Exception)
        print("1 saniye sonra tekrar denenecek")
        time.sleep(1)
        loginTryer()


def goToSite(link):
    try:
        print(link)
        browser.get(link)
    except Exception:
        print("Hata olustu", "       ", Exception)
        print("1 saniye sonra tekrar denenecek")
        time.sleep(1)
        goToSite(link)


def getAllPosts():
    goToSite("https://www.instagram.com/gelecekbilimde")
    time.sleep(3)
    source = browser.page_source
    bs = BeautifulSoup(source, "lxml")
    dicProfileInfos = getProfileInfos(bs)
    allPosts = bs.find_all("div", {"class": "v1Nh3 kIKUG _bz0w"})
    allLinks = []
    for i in allPosts:
        allLinks.append("https://www.instagram.com"+i.find("a")["href"])
    returnData = {
        "allPosts": allLinks,
        "postCounter": dicProfileInfos["posts"],
        "followerCounter": dicProfileInfos["followers"],
        "followedCounter": dicProfileInfos["followed"]
    }
    return returnData


def getProfileInfos(bs):
    allPosts = bs.find_all("span", {"class": "g47SY"})
    dic = {
        "posts": allPosts[0].text,
        "followers": allPosts[1]["title"],
        "followed": allPosts[2].text
    }
    return dic


def saveUpdates(newData):
    mydate = datetime.datetime.now()
    nowDay = mydate.strftime("%x").split("/")
    data = json.dumps(newData)
    file = open(
        f"./{getTime()[0]}-{str(getTime()[1].split('.')[0]).replace(':','-')}.json", "w+", encoding="UTF-8")
    file.write(data)
    file.close()


def get_Data():
    try:
        instagram = open(
            f"./{getTime()[0]}.json", "r+", encoding="UTF-8")
        data = json.load(instagram)
    except:
        instagram = open(
            f"./{getTime()[0]}.json", "w+", encoding="UTF-8")
        data = []
    instagram.close()
    return data


def getTime():
    tz_Turkey = pytz.timezone('Turkey')
    mydate = str(datetime.datetime.now(tz_Turkey)).split(" ")
    return mydate


def getPostInfos(allLinks):
    allData = []
    for i in allLinks:
        goToSite(i)
        time.sleep(3)
        try:
            source = browser.page_source
            bs = BeautifulSoup(source, "lxml")
            # tag section
            tags = bs.find_all("a", {"class": "xil3i"})
            tagList = []
            for x in tags:
                tagList.append(x.text)
            # Like section
            likes = bs.find_all(
                "div", {"class": "_7UhW9 xLCgt qyrsm KV-D4 fDxYl T0kll"})[0].text.split(" ")[0]
            date = getTime()
            obj = {
                "link": i,
                "tarih": date[0],
                "saat": date[1],
                "tags": tagList,
                "likes": likes
            }
            allData.append(obj)
        except:
            print("Post data err")
        time.sleep(3)
    return allData


def process():
    browser.maximize_window()
    loginTryer()
    loginSkipButtonFun()
    time.sleep(2)
    profileInfos = getAllPosts()
    allLinks = checkAndGetLinks(profileInfos)
    allPostInfo = getPostInfos(["https://www.instagram.com/p/CY6HWUnN2se"])
    obj = {"saat": getTime()[1],
           "postCounter": profileInfos["postCounter"],
           "followerCounter": profileInfos["followerCounter"],
           "followedCounter": profileInfos["followedCounter"],
           "allPostInfo": allPostInfo
           }
    saveUpdates([obj])
    browser.close()


def checkAndGetLinks(data):
    with open("links.txt", "r+", encoding="utf-8")as file:
        links = file.readlines()
        parsedLinks = list()
        for i in links:
            parsedLinks.append(i.split('\n')[0].split()[0])
        for i in data["allPosts"]:
            if not i in parsedLinks:
                print(i)
                parsedLinks.append(i)
                file.write(i)
                file.write("\n")
    return parsedLinks


objModel = {}

process()
