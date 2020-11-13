from function import *

client = Client()
poll = client.openPolling()

admin = ["U468b5a4827b5620266b9b11502619be6"]
settings = {
        "changeBot":False
    }

def restartBot():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return str(result_str)

def contactBroadcast(fr, text):
    c = client.getContactList()
    for i in range(len(c)):
        to = c[i]['contactId']
        time.sleep(1)
        client.sendMessage(to, text)
    client.sendMessage(fr, "Done")

def contactBroadcastWithImage(fr, imageUrl, text):
    c = client.getContactList()
    n = get_random_string(10)
    nama = n + ".jpg"
    urllib.request.urlretrieve(imageUrl, nama)
    for i in range(len(c)):
        to = c[i]['contactId']
        client.sendFileWithPath(to, nama)
        client.sendMessage(to, text)
        time.sleep(1)
    os.remove(nama)
    client.sendMessage(fr, "Done")

with poll.getresponse() as response:
    while not response.closed:
        for chunk in response:
            #print(chunk)
            if "data:{" in chunk.decode('utf-8'):
                chnk = json.loads(chunk.decode('utf-8').replace("data:",""))
                event = chnk["event"]
                if event == "chat" and "subEvent" in chnk and chnk["subEvent"] == "message":
                    botId = chnk["botId"]
                    msg = chnk["payload"]["message"]
                    chatId = chnk["payload"]["source"]["chatId"]
                    if "userId" in chnk["payload"]["source"]:
                        sender = chnk["payload"]["source"]["userId"]
                    if msg["type"] == "text":
                        text = msg["text"]
                        #cmd = text.lower()
                        cmd = text
                        if cmd.lower() == "hello":
                            if sender in admin:
                                client.sendMessage(chatId, "halo")
                            else:
                                client.sendMessage(chatId, "hai")
                        elif cmd == "!listBot":
                            if sender in admin:
                                listBot = client.getBots()
                                a = ""
                                for i in range(len(listBot)):
                                    s = i+1
                                    a += str(s)+". "+str(listBot[i]["name"]+"\n")
                                client.sendMessage(chatId, a)
                            else:
                                client.sendMessage(chatId, "Mo Ngapain,...??")
                        elif cmd.startswith("!changebot "):
                            if sender in admin:
                                try:
                                    spl = cmd.split(" ")
                                    credential = client.readJson("credential.json")
                                    bots = client.getBots()
                                    no = int(spl[1])
                                    for i in range(len(bots)+1):
                                        if i == no:
                                            choice = i-1
                                            credential["mid"] = bots[choice]['botId']
                                            credential["userId"] = bots[choice]['basicSearchId']
                                            credential["name"] = bots[choice]['name']
                                            client.writeJson("credential.json", credential)
                                        else:
                                            pass
                                    client.sendMessage(chatId, "Berhasil beralih ke "+credential['name']+"\nLink line://ti/p/"+credential["userId"])
                                    client.sendMessage(chatId, "Tunggu beberapa saat,...")
                                    restartBot()
                                except Exception as asu:
                                    client.sendMessage(chatId, str(asu))
                            else:
                                client.sendMessage(chatId, "Mo Ngapain,...??")
                        elif cmd.startswith("!ex"):
                            if sender in admin:
                                com = cmd.replace("!ex","")
                                try:
                                    exec(com)
                                except Exception as err:
                                    client.sendMessage(chatId, str(err))
                            else:
                                client.sendMessage(chatId, "Hayoo mo ngapain :v")
                        elif cmd.startswith("!cbc: "):
                            if sender in admin:
                                tes = cmd.replace("!cbc: ", "")
                                try:
                                    contactBroadcast(chatId, str(tes)+"\n\n\nFree BC OA\n[Powered by SDK]")
                                except Exception as asu:
                                    client.sendMessage(chatId, str(asu))
                            else:
                                client.sendMessage(chatId, "Hayoo mo ngapain :v")
                        elif cmd.startswith("!ibc: "):
                            if sender in admin:
                                tes = cmd.replace("!ibc: ", "")
                                tes = tes.split(" && ")
                                link = tes[0]
                                te = tes[1]
                                try:
                                    contactBroadcastWithImage(chatId, link, str(te)+"\n\n\nFree BC OA\n[Powered by SDK]")
                                except Exception as asu:
                                    client.sendMessage(chatId, str(asu))
                            else:
                                client.sendMessage(chatId, "Hayoo mo ngapain :v")
                    elif msg["type"] == "image":
                        contentHash = msg["contentProvider"]["contentHash"]
                        url = client.generateContentHashUrl(contentHash)
                        client.sendMessage(chatId, url)
                            
                elif event == "chat" and "subEvent" in chnk and chnk["subEvent"] == "chatRead":
                    chatId = chnk["payload"]["source"]["chatId"]
                    # READ DETECTION
                    
                else:
                    pass
                    # print(chunk)
                    # OPERATION
                    # NEED PARSING FOR MORE FEATURE
                    # DO IT WITH URE SELF :D
