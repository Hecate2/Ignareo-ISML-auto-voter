# ISML_auto_voter
Python 3.6 √  Python 3.7 ✘  
https://github.com/Hecate2/ISML_auto_voter  
  
驱逐舰伊格那雷奥，用于世萌高速自动投票  
Destroyer Ignaleo(IGN): Vote automatically at ISML, www.internationalsaimoe.com/voting  
  
**无论世萌，B萌，部落萌，贴吧萌，一切萌战都是刷票！而只有刷票能对抗刷票。**  
**Voters of all lands, UNITE!**  
  
Sep. 19th, 2019: Please do not start thousands of selenium browsers in a few seconds. They exhausts the output bandwidth of ISML.  
Today I spammed no more than 130 votes after Misaka Mikoto asked me for a manual vote but I encountered 3 session expires in a row.  
Please switch to latest technologies to save the hardware resources of ISML, which does good to everyone. I believe IGN causes no expired session even at 200 votes per minute. 
  
Sep. 13th, 2019: >asyncio.ensure_future(self._post('httpc://chtholly.68',data=r'祝妖精仓库中秋快乐！'.encode('月饼')))  
July 19th, 2019: Welcome to the novel (under GPL-3.0 license) at /DestroyerIGN/CINT the Space Fleet Hecate2  
欢迎阅读DestroyerIGN附赠的小说！(按GPL-3.0开源协议发布)  
https://github.com/Hecate2/ISML_auto_voter/raw/master/DestroyerIGN/CINT%20the%20Space%20Fleet%20Hecate2%20(%E6%9C%AA%E9%85%8D%E4%B9%90).docx  
**For more information: log.md**
  
## Brief introduction:  
Screaming high concurrency! Light weight Convolutional Neural Network! Against captcha within 0.06 seconds per image on CPU! 
Easy for distributed deployment!  
  
The structure of IGN can be applied for any saimoe voting and even more in principle (I'm using IGN to monitor IoT devices). Using IGN for other purposes is also welcomed. **Feel free to raise** ***Issues*** **including "我永远喜欢珂朵莉", "I love Chtholly forever", "私はいつまでもクトリが好きです", and even more!** （请扭曲的珂学家不要一夜之间刷两千条……）  
However, **BE CAREFUL in case your operations may result in a CC attack!** (I've killed an SQL service imprudently with IGN...)  
  
I have already developed an auto voter in the year 2018, using scrapy. Destroyer IGN, as a state-of-art, is re-designed for the future. 
As a result, IGN has never encountered any real battle in ISML till now (July 6th, 2019).   
  
**Before you challenge a rich supporting group, you should always consider such a probable fact: though IGN can support 2500 to 5000 voters on your computer, your opponent has hundreds of machines, each can run 25 to 50 selenium browsers. Meanwhile, you can't afford the cost for proxies.**  
  
## How to use:  
In DestroyerIGN, start **captchaServer.py**, and then **Ignaleo.py**. 
Finally, provide Destroyer Ignaleo with ammunition (proxy ips) by starting **Ammunition.py**.  
**IGN does not open fire until you run Ammunition.py at last!**  
  
## The structure:  
IGN is fabricated with 3 cascades:  
data producer -> main network IO -> servers for computation intensive tasks  
Every later cascade is an http server for the previous one.  
  
When running IGN, the main IO receives POST from the proxy provider, and directly contact ISML with http requests.  
The captcha server receives POST from the main IO, and recognizes the letters and digits in the captcha image.  
  
To change which characters to vote for, modify **charaSelector.py**.  
To control the network IO process of voting, or use IGN for other purposes, write your own codes in **Voter.py**.  
To deploy multiple processes of servers, change **portList** in Ammunition.py, Ignaleo.py and captchaServer.py.  
To tackle Cloudflare IUAM firewall (Checking your browser before…), try to extract the JavaScript carefully, using **aiocfscrape.py**. The original version offered by https://github.com/pavlodvornikov/aiocfscrape have been disabled since Cloudflare changes the firewall very often. You may refer to all the resources from Github to bypass the firewall.   
  
## Accessories: 
**ISMLnextGen**, which contains some prototypes and basic code blocks, is the lab for the development of IGN.  

# Acknowledgement
First of all, please allow me to extend my sincerest gratitude to  
<font color=#0099ff>Chtholly Nota Seniorious</font>  
and  
<font color=DodgerBlue>Shino Asada</font>,  
who always charge my will to conquer all the difficulties.  
  
Thanks to my supporting group, which invested huge funds to give birth to the previous generations of auto voter programs.
Thanks for their trust and cultivation on me.  
  
Thanks to ISML, as well as other saimoes, 
which gives me the opportunity and an arena to practice on web spiders and other technologies. 
Perhaps saimoes in the future should give up deciding who is the most moe, and focus more on training programmers.  

Thanks to some of my opponents in saimoe, who developed brilliant programs to inspire and spur on me.  
  
Thanks to all the ***Chthollists*** who love Chtholly and SukaSuka.  
  
本程序很多方面为了便于部署、计算，降低硬件门槛，而牺牲了极限性能。谨代表珂朵莉和威廉练剑所发挥的最低水平！  
  
# Tips! Important for the most wealthy voters!
0. Spamming **TOO MANY** votes is usually meaningless, except for burning your own $dollars, making difficulties for ISML operaters, and delaying the following matches.  
1. Think before you cast billions of votes in a few minutes. If you really would like to spam, spread your votes to the whole 24 hours. Quick spamming are sure to be recognized by ISML operators.  
2. Think twice if you want to challenge any character. You should disguise yourself very well, and you know you may get revenged.  
3. ~~Think three times if you want to vote billions against the wish of ISML operators.~~ The justical operators have the right to ignore your votes without certain proof!  
4. Think four times if you want to challenge some super-rich supporting groups. The cost for employing programmers is just a piece of cake for them, since they have hundreds of thousands of budget for all kinds of saimoes! Well, that is not at all a large sum of money if everyone burns cash with IGN, but you should always assume that they have 1 mol (6.02×10^23) of money.   
5. Think five times before you launch IGN, because IGN drains everyone's life and wealth. You are a human instead of a Leprechaun!  
6. IGN is designed to create a nuclear balance and deprive the monopoly of some evil supporting groups. I don't mind your bombing them with IGN, but please **VOTE BY HAND**, and **DON'T spam irresponsibly with IGN** if you really intend to support me! Nobody gains real happiness through a nuclear war! If you really have to spam against the evil, think about all the factors carefully.  
7. Vote **(by hand!)** for Chtholly Nota Seniorious if you really love her!  
8. 有钱请捐给世萌，不要捐给代理ip供应商或者大厨。Donate your billions of dollars to ISML instead of proxy suppliers! Never buy a spamming service from rich supporting groups!  
  
Remember that: Nobody is with almighty justice. Nobody sees the end of war until death.  
  
Again: Thank you very much for fighting against all the bad civilizations in all kinds of saimoes!  
