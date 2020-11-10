import requests, json, time, urllib.parse, cv2, numpy, http.client, random, string, io, sys

class Client():
    def __init__(self):
        self.defaultHeaders = {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
        self.session = requests.session()
        self.tempData = {}
        self.loginWithQrCode()
        self.loadSession()

    def readJson(self, filename):
        with open(filename) as f:
            return json.load(f)

    def writeJson(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data,f,indent=4,sort_keys=True)

    def readQrCode(self, raw):
        img_array = numpy.asarray(bytearray(raw), dtype=numpy.uint8)
        im = cv2.imdecode(img_array, 0)
        det = cv2.QRCodeDetector()
        retval, points, straight_qrcode = det.detectAndDecode(im)
        return retval

    def loadSession(self):
        credential = self.readJson("credential.json")
        self.session.cookies.set('ses', credential["authToken"])
        if "mid" not in credential:
            bots = self.getBots()
            if bots == []:
                print("[ ERROR ] No bot found on your account!!!")
                sys.exit()
            for n in range(len(bots)):
                print(str(n+1)+'. '+bots[n]["name"])
            choice = int(input("Please Select Account: "))-1
            credential["mid"] = bots[choice]['botId']
            credential["userId"] = bots[choice]['basicSearchId']
            credential["name"] = bots[choice]['name']
            self.writeJson("credential.json", credential)
        self.mid = credential["mid"]
        self.userId = credential["userId"]
        self.getCsrfToken()
        print("[ NOTIF ] Success login...")
        check = self.getChatMode()
        if 'code' in check:
            print("[ ERROR ] Please set bot to chat mode!!!")
            sys.exit()
        
    def loginWithQrCode(self):
        credential = self.readJson("credential.json")
        if "authToken" not in credential:
            _csrf = self.session.get(
                        url='https://account.line.biz/login?redirectUri=https%3A%2F%2Fchat.line.biz%2F',
                        headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'Connection': 'keep-alive', 'Host': 'account.line.biz', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=True
                        ).text.split('name="x-csrf" content="')[1].split('"')[0]
            
            redir = self.session.post(
                        url='https://account.line.biz/login/line?type=login',
                        headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'max-age=0', 'Connection': 'keep-alive', 'Host': 'account.line.biz', 'Origin': 'https://account.line.biz', 'Referer': 'https://account.line.biz/login?redirectUri=https%3A%2F%2Fchat.line.biz%2F', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data={"_csrf": _csrf},
                        allow_redirects=False
                        ).headers["location"]
            
            auth_url = self.session.get(
                        url=redir,
                        headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'cache-control': 'max-age=0', 'referer': 'https://account.line.biz/', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'cross-site', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=False
                        ).headers["location"]

            _state = urllib.parse.unquote(auth_url).split('&state=')[1].split('&')[0]
            _loginState = urllib.parse.unquote(auth_url).split('loginState=')[1].split('&')[0]

            redir = self.session.get(
                        url=auth_url,
                        headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'cache-control': 'max-age=0', 'cookie': 'loginState=N8ovqhoa5fRKNP9PbHIzWi', 'referer': 'https://account.line.biz/', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'cross-site', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=True
                        ).url
            
            qrCode = json.loads(self.session.get(
                        url='https://access.line.me/qrlogin/v1/session?_='+str(int(time.time()))+'&channelId=1576775644',
                        headers={'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'referer': redir, 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=True
                        ).text)["qrCodePath"]
            
            downloadData = self.session.get(
                        url="https://access.line.me"+qrCode,
                        headers={'accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'referer': redir, 'sec-fetch-dest': 'image', 'sec-fetch-mode': 'no-cors', 'sec-fetch-site': 'same-origin', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=True
                        ).content
            qrLink = self.readQrCode(downloadData)
            print("Your QR link: "+qrLink)
            
            pinCode = json.loads(self.session.get(
                        url='https://access.line.me/qrlogin/v1/qr/wait?_='+str(int(time.time()))+'&channelId=1576775644',
                        headers={'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'referer': redir, 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=True
                        ).text)["pinCode"]
            print("Your pincode: "+pinCode)

            pinCodeCallback = self.session.get(
                        url='https://access.line.me/qrlogin/v1/pin/wait?_='+str(int(time.time()))+'&channelId=1576775644',
                        headers={'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'referer': redir, 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=True
                        )   
            qrPinCert = pinCodeCallback.headers["set-cookie"].split('qrPinCert=')[1].split(";")[0]
            cert = pinCodeCallback.headers["set-cookie"].split('cert=')[1].split(";")[0]

            _csrf = self.session.cookies.get_dict()["X-SCGW-CSRF-Token"]
            authLogin = self.session.get(
                        url='https://access.line.me/oauth2/v2.1/qr/authn?loginState='+_loginState+'&loginChannelId=1576775644&returnUri=%2Foauth2%2Fv2.1%2Fauthorize%2Fconsent%3Fscope%3Dprofile%26response_type%3Dcode%26state%3D'+_state+'%26redirect_uri%3Dhttps%253A%252F%252Faccount.line.biz%252Flogin%252Fline-callback%26client_id%3D1576775644&__csrf='+_csrf,
                        headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'referer': auth_url, 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=False
                        )
            authLogin_redir = self.session.get(
                        url=authLogin.headers["location"],
                        headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9', 'referer': auth_url, 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=False
                        )
            authLogin_result = self.session.get(
                        url=authLogin_redir.headers["location"],
                        headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'Connection': 'keep-alive', 'Host': 'account.line.biz', 'Referer': 'https://access.line.me/', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'},
                        data=None,
                        allow_redirects=False
                        )
            credential["authToken"] = authLogin_result.headers["Set-Cookie"].split(";")[0].replace("ses=","")
            self.writeJson("credential.json", credential)

    def getCsrfToken(self):
        _csrf = json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/csrfToken',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["token"]
        self.defaultHeaders["x-xsrf-token"] = _csrf

    def getChatMode(self):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/settings/chatMode',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def getOwners(self):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/owners',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["list"]
    
    def getBots(self):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots?noFilter=true&limit=1000',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["list"]
    
    def getMessages(self, chatId):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/messages/'+chatId,
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["list"]

    def getImageMessages(self, chatId):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/messages/'+chatId+'/swipeViewer',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["list"]

    def getMediaInfo(self, messageId):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/messages/content/'+messageId+'/info',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def getChat(self, chatId):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId,
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def getChatList(self, folderType='ALL'): # ['NONE', 'ALL', 'INBOX', 'UNREAD', 'FOLLOW_UP', 'DONE', 'SPAM']
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats?folderType='+folderType+'&tagIds=&limit=25',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def markAsRead(self, chatId):
        return json.loads(self.session.put(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/markAsRead',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def addFollowedUp(self, chatId):
        return json.loads(self.session.put(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/followUp',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def deleteFollowedUp(self, chatId):
        return json.loads(self.session.delete(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/followUp',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def addResolved(self, chatId):
        return json.loads(self.session.put(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/done',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def deleteResolved(self, chatId):
        return json.loads(self.session.delete(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/done',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def addSpam(self, chatId):
        return json.loads(self.session.put(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/spam',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def deleteSpam(self, chatId):
        return json.loads(self.session.delete(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/spam',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def getManualChatStatus(self, chatId):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/useManualChat',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def leaveChat(self, chatId):
        return json.loads(self.session.post(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/leave',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def deleteChat(self, chatId):
        return json.loads(self.session.delete(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId,
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)
    
    def getContactList(self):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/contacts?query=&sortKey=DISPLAY_NAME&sortOrder=ASC&excludeSpam=true&limit=100',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["list"]
    
    def getMembersOfChat(self, chatId):
        return json.loads(self.session.get(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/chats/'+chatId+'/members?limit=100',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)["list"]
    
    def sendMessage(self, chatId, text):
        data = {"type":"text","text":text,"sendId":chatId+"_"+str(int(time.time()))+"_"+''.join(random.choice(string.digits) for i in range(8))}
        return json.loads(self.session.post(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/messages/'+chatId+'/send',
            headers=self.defaultHeaders,
            json=data,
            allow_redirects=True
            ).text)

    def sendSticker(self, chatId, packageId, stickerId):
        data = {"stickerId":stickerId,"packageId":packageId,"type":"sticker","sendId":chatId+"_"+str(int(time.time()))+"_"+''.join(random.choice(string.digits) for i in range(8))}
        return json.loads(self.session.post(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/messages/'+chatId+'/send',
            headers=self.defaultHeaders,
            json=data,
            allow_redirects=True
            ).text)

    def sendFileWithPath(self, chatId, path):
        data = {"file": open(path, 'rb'), "sendId":(None, chatId+"_"+str(int(time.time()))+"_"+''.join(random.choice(string.digits) for i in range(8)))}
        return json.loads(self.session.post(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/messages/'+chatId+'/sendFile',
            headers=self.defaultHeaders,
            files=data,
            allow_redirects=True
            ).text)

    def generateContentHashUrl(self, contentHash):
        return 'https://chat-content.line-scdn.net/bot/'+self.mid+'/'+contentHash
    
    def streamingApiToken(self):
        return json.loads(self.session.post(
            url='https://chat.line.biz/api/v1/bots/'+self.mid+'/streamingApiToken',
            headers=self.defaultHeaders,
            data=None,
            allow_redirects=True
            ).text)

    def openPolling(self, ping=60):
        dataStream = self.streamingApiToken()
        streamingApiToken = dataStream["streamingApiToken"]
        lastEventId = dataStream["lastEventId"]
        lastEventTimestamp = dataStream["lastEventTimestamp"]
        poll = http.client.HTTPSConnection('chat-streaming-api.line.biz')
        poll.request('GET', '/api/v1/sse?token='+streamingApiToken+'&deviceToken=&deviceType=&clientType=PC&pingSecs='+str(ping)+'&lastEventId='+lastEventId, headers=self.defaultHeaders)
        return poll
        

