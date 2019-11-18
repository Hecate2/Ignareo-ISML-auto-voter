# ISML_auto_voter
*To love another person is to see the face of God.*  
  
Python 3.6 √  Python 3.7 √  
https://github.com/Hecate2/ISML_auto_voter  
  
驱逐舰伊格那雷奥，用于世萌高速自动投票  
Destroyer Ignaleo(IGN): Vote automatically at ISML, www.internationalsaimoe.com/voting  
  
**无论世萌，B萌，部落萌，贴吧萌，一切萌战都是刷票！而只有刷票能对抗刷票。**  
**Voters of all lands, UNITE!**  
Nov. 18th, 2019: Time for academic punk!  
Quite a few have requested the CNN training codes. I'm too exhausted to write instructions, so help yourself! The main training dataset is currently not available.  
Minimum recommendation of GPU: one GTX1080ti  
Minimum recommendation of traning set: 3,000 to 10,000 effective samples.  
Many thanks to all who sacrificed for Chtholly and something named "justice".  
  
Nov 14th: 1th anniversary for the asynchronous prototype.   
  
Nov 1st: SukaMoka 08 is really enjoyable! But as far as I know, not every reader wants Chtholly to come to life again.  
  
Oct. 23rd, 2019: To those who sell or rent out my captcha servers carelessly: **PLEASE READ THE LICENSE!**  
A supporting group of a mighty character(not Chtholly) has improved the accuracy of the captcha system, at a heavy cost of CPU time(0.2 to 0.4 seconds per image, using only 1 CPU core) and 1 month of intensive brain work. This might be academically a nice job, but not always the best for actual battles. In my opinion, reducing the cost of I/O should still be the priority for most spammers. You may find a more impeccable pretreatment for captchas to reduce the number of images downloaded. Those owning professional techniques, nuclear power plants and tons of powerful GPUs can try **scene text recongnition** to achive ultimate accuracy and download one captcha image.  
I'm still waiting for ISML to take **effective** anti-spamming measures. Effective measures have to be carried out for the survival of ISML. If a 'Moore's Law' can be kept by spammers, then in Oct. 2020, it will be likely that people scan billions of free proxies from the Internet with `masscan` or `zmap`, and a bandwith of no less than 10Gbps.  
  
Oct. 21st, 2019: `libuv`最高！  
  
Oct. 12th, 2019: *Ignaleo.py* will be **renamed** as ***IgnaleoA.py***. **The name *Ignaleo* now refers to the whole series of programs.**  
  
Sep. 25th, 2019: ISML, ありがとう。  
**Contact me to apply for IgnaleoG.py. It can bypass Cloudflare IUAM fireawall, and utilize your proxies at a much higher efficiency.** Certainly I am not to offer it for free to the evil opponents of Chtholly.  
Civil uses of IgnaleoG are welcomed! Just don't attack Chtholly in all kinds of saimoe events.  

Sep. 19th, 2019: Please do not start thousands of selenium browsers in a few seconds. They exhaust the output bandwidth of ISML.  
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
In DestroyerIGN, start **captchaServer.py**, and then **IgnaleoA.py**. 
Finally, provide Destroyer Ignaleo with ammunition (proxy ips) by starting **Ammunition.py**.  
**IGN does not open fire until you run Ammunition.py at last!**  
For civil use of Ignaleo, contact me to apply for **IgnaleoG**. IgnaleoA is not fully reliable when thousands of connections have to be handled in a single process, especially on Windows.  
(I can't publish IgnaleoG at present because G probably leaves no way for ISML to make a living.)  
  
## The structure:  
IGN is fabricated with 3 cascades:  
data producer -> main network IO -> servers for computation intensive tasks  
Every later cascade is an http server for the previous one.  
  
When running IGN, the main IO receives POST from the proxy provider, and directly contact ISML with http requests.  
The captcha server receives POST from the main IO, and recognizes the letters and digits in the captcha image.  
  
To change which characters to vote for, modify **charaSelector.py**.  
To control the network IO process of voting, or use IGN for other purposes, write your own codes in **Voter.py**.  
To deploy multiple processes of servers, change **portList** in Ammunition.py, IgnaleoA.py and captchaServer.py.  
To tackle Cloudflare IUAM firewall (Checking your browser before…), try to extract the JavaScript carefully, using **aiocfscrape.py**. The original version offered by https://github.com/pavlodvornikov/aiocfscrape have been disabled since Cloudflare changes the firewall very often. You may refer to all the resources from Github to bypass the firewall.   
  
## Accessories: 
**ISMLnextGen**, which contains some prototypes and basic code blocks, is the lab for the development of IGN.  

# Acknowledgement
First of all, please allow me to extend my sincerest gratitude to  
<font color=#0099ff>Chtholly Nota Seniorious</font>,  
Tiat Siba Ignaleo,  
Ithea Myse Valgulious,  
Nephren Ruq Insania,  
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
  
# Tips! What if ISML responds very slowly?  
First, please allow me to ascribe the reason dogmatically to spammers using pristine selenium wildly.  
By running a miniature version of stress test involving a mixture of selenium, multi-thread spamming programs and IGN, I would like to give the following suggestion:
> **STOP USING IGN** when ISML is really slow. If you persist reloading IGN with ammunition very quickly, it can be extremely difficult for everyone (both humans and programs) to submit vote. I mean **Neither bots nor humans can submit**! And ISML would receive very little votes for hours, until someone quit.  
  
**But why?**  
Well, selenium and multi-thread web spiders has a ***limited*** number of "**workers**" (the word may refer to either processes or threads), but the number of workers of IGN is ***almost unlimited***.  
When the billions of requests launched by voting programs are not responded, the requests are certainly kept in the program, waiting. Exerting pressure on a server with limited "workers" can hardly lead to a Denial of Service, because they do not start new spamming attempts when all the workers have to wait. So most of the workers can receive their responses sooner or later. But IGN doesn't care about slow responses and keep raising more attempts. With the passage of time (perhaps within only a few minutes in actual battles), it is likely that IGN would own the absolute major portion of unresponded requests, which will be far more than what ISML can handle. The increase of unresponded requests, however, gives even more positive feedback to generating unhandled spamming attempts, since IGN does not care about the unresponded ones! Only the timeout and the failure of proxies can stop IGN from holding more requests.  
> And do not assume yourself as the undisputed winner when you take up all the hardware resources of ISML with your ancient spamming programs. You can't exclude IGN at all, but you rile everyone.  
  
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
