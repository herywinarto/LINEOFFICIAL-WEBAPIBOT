from function import *

client = Client()
poll = client.openPolling()
with poll.getresponse() as response:
    while not response.closed:
        for chunk in response:
            if "data:{" in chunk.decode('utf-8'):
                chunk = json.loads(chunk.decode('utf-8').replace("data:",""))
                event = chunk["event"]
                if event == "chat" and "subEvent" in chunk and chunk["subEvent"] == "message":
                    msg = chunk["payload"]["message"]
                    chatId = chunk["payload"]["source"]["chatId"]
                    if msg["type"] == "text":
                        text = msg["text"]
                        cmd = text.lower()
                        if cmd == "hello":
                            client.sendMessage(chatId, "hai")
                            
                elif event == "chat" and "subEvent" in chunk and chunk["subEvent"] == "chatRead":
                    chatId = chunk["payload"]["source"]["chatId"]
                    # READ DETECTION
                    
                else:
                    print(chunk)
                    # OPERATION
                    # NEED PARSING FOR MORE FEATURE
                    # DO IT WITH URE SELF :D
