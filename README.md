# ISML_auto_voter
Python 3.6 √  Python 3.7 ✘  
https://github.com/Hecate2/ISML_auto_voter  
  
驱逐舰伊格那雷奥，用于世萌高速自动投票  
Destroyer Ignaleo(IGN): Vote automatically at ISML, www.internationalsaimoe.com/voting  
  
**无论世萌，B萌，贴吧萌，一切萌战都是刷票！而只有刷票能对抗刷票。**  
**Voters of all lands, UNITE!**  
  
July 29th, 2019: >asyncio.ensure_future(self._post('httpc://chtholly.68',data=r'冰柠檬茶'.encode('三分糖')))  
  
July 28th, 2019: Nice to see no massive spamming votes yesterady.  
  
July 27th, 2019: **Best wishes for those who obey the rules!**  
  
July 19th, 2019: Welcome to the novel at /DestroyerIGN/CINT the Space Fleet Hecate2  
欢迎阅读DestroyerIGN附赠的小说！  
  
July 12nd, 2019: **It's quite intelligible that some of you do not believe the enormous scale of auto voting, or you may suspect the performance of my program. That's why I realease:**  
**我知道有的人不相信萌战刷票有多恐怖，或者不相信我的程序投票的速度，所以又发射了这枚小核弹供吃瓜群众参考：**  
https://github.com/Hecate2/ISML_auto_voter/releases/download/20190125/20190125x32187.PSWD.Rem00.7z  
for your reference. As far as I know, the total number of votes in 24 hours should be at least hundreds of thousands, or millions. The maximum number is quite limited by the hardware of ISML, instead of voting programs.  
  
## Brief introduction:  
Screaming high concurrency! Light weight Convolutional Neural Network! Against captcha within 0.06 seconds per image on CPU! 
Easy for distributed deployment!  
  
The structure of IGN can be applied for any saimoe voting and even more in principle. Using IGN for other purposes is also welcomed.  
However, **BE CAREFUL in case your operations may result in a CC attack!**  
  
I have already developed an auto voter in the year 2018, using scrapy. Destroyer IGN, as a state-of-art, is re-designed for the future. 
As a result, IGN has never encountered any real battle in ISML till now (July 6th, 2019).  
However, I do hope IGN no longer have to make contact with the wild saimoe opponents anymore.  
  
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
  
## Accessories: 
**ISMLnextGen**, which contains some prototypes and basic code blocks, is the lab for my development of IGN.  

# **Acknowledgement**
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
