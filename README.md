# Destroyer Ignareo (IGN)  

*To love another person is to see the face of God.*  

https://github.com/Hecate2/ISML_auto_voter  or https://github.com/Hecate2/Ignareo

Ultimate High-performance HTTP I/O originated for Chtholly Nota Seniorious, and for ISML, www.internationalsaimoe.com/voting.  

Launches **100k（十万）HTTP requests in < 0.7 seconds** on a single 4GHz Ryzen 3600 core with 3200MHz memory. 

Python 3.6 √ 

Python 3.7 √  (recommended, for better SSL experience)

对于Windows Python3.8用户
For users using Python 3.8 on Windows

```
import platform  
if platform.system() == "Windows":  
    import asyncio  
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  
```
您可能需要增加这些代码解决`NotImplementedError`。 
You probably need to include these code to solve the `NotImplementedError`

**无论世萌，B萌，部落萌，贴吧萌，一切萌战都是刷票！而只有刷票能对抗刷票。**  
**Voters of all lands, UNITE!**  

**Thanks to the increasing stars, I have decided to rewrite this README to be civil-programmer-oriented.**

<u>**Feel free to raise** ***Issues*** **including "我永远喜欢珂朵莉", "I love Chtholly forever", "私はいつまでもクトリが好きです".**</u>

Codes in this repository were initially written for voting in ISML. Consequently, everything was rapidly edited with simple tools including IDLE and notepads, designated for intensive fire power instantly launched by **anyone (even non-programmers)** only with a double click on Windows. Therefore, the codes might be not well formatted, not quite programmer-flavored and redundant. I apologize for that.

## Tutorial for civil users  

```gevent.spawn(a_function_with_socket_operations, param, param, parameters…)```  
~~and that's all you need!~~  

Ignareo is still a bare core for now, but it is essentially different from and can never be replaced with other libraries like `scrapy` and `grequests`. I have been looking for methods of further integration, but integration sacrifices transparency and simplicity. Therefore I will **not** pack Ignareo as a series of APIs or as a scrapy-like engine. 

Generally speaking, I'm sorry but **you may have to read the source code** of `DestroyerIGN/IgnareoG.py`, because **reconstructing Ignareo for your own use requires an understanding of its structure**. Feel free to copy any code to shape your components.  

#### The good news is that **I'll guide you through the source code in the following example**.

##  How to vote in ISML with Ignareo:  

This is the original "military" purpose for which I built Ignareo. Civil users do not need to actually run the codes, but may follow this as an example.

### How can I just start to vote?

In `./DestroyerIGN`, start **captchaServer.py**, and then **IgnareoG.py**. 
Finally, provide Destroyer Ignareo with ammunition (proxy IPs) by starting **Ammunition.py**.   

**For new hands:** Note that you should tell `Ammunition.py` where to get the proxies at what frequency. You may find tens of thousands of free proxies or purchase millions from the Internet. Search for `55556` in `Ammunition.py` and you would find tuples like `('http://localhost:55556/',1),`. Substitute the default tuples for your own URLs and time intervals (in seconds) to get proxies. `Ammunition.py` visits your URL and extracts `XXX.XXX.XXX.XXX:XXXXX` from the webpage, and send the proxies in the format `XXX.XXX.XXX.XXX:XXXXX\r\nXXX.XXX.XXX.XXX:XXXXX\r\n...`. 

**IGN does not open fire until you run Ammunition.py at last!**  

You can also try `IgnareoA.py` implemented with `asyncio`, but **IgnareoA is not fully reliable** when thousands of concurrent connections have to be handled in a single process, especially on Windows, because **the number of files that `asyncio` can open is limited**. But IgnareoA saves a little bit of memory and CPU than IgnareoG. 

`IgnareoMT` implemented with threads may also be a choice, but **the performance is significantly lower**. And **IgnareoMT** **leads to memory leak in long run**. You have to restart your computer to recollect free memory. 

The order in which the three engines were built is:

[earliest] A → MT → G [latest]

### The technical steps to vote in ISML

This part guides you to cast a simulated machine vote with HTTP requests. Assume that you are a real human voter who visits https://www.internationalsaimoe.com/voting , and you are given a long list of characters to select. After you select the characters, you should **fill the CAPTCHA**. You **should spend at least 90 (or 120, 180, 190) seconds before you are allowed to submit** your vote. To prevent anyone to cast multiple votes in a match, **only one vote is allowed from a same IP address**. 

During the process stated above, your browser sends HTTP requests to the ISML server. Now we are to simulate your browser's HTTP operations with Ignareo. So, from the perspective of HTTP requests, what happens in the process described above? 

- When you visit the ISML website:

  Your browser sends an HTTP GET request to http://www.internationalsaimoe.com/voting , and the server responds an HTML where all the characters are listed. This can be simulated with

  ```python
  r = requests.get('http://www.internationalsaimoe.com/voting')
  ```

  And `r.text` is the HTML you want. **Note that the codes given in this chapter is just a conceptual example, not the best practice in real voting.**

  Besides, in order to distinguish "who you are", a "voting_token" is given in the responded HTML to identify you. If your IP address has already casted a vote before, you will not be given the token.

  Now we have to wait for 90 (or 120, 180, 190) seconds before we submit the vote. For now we are just to record the time when we acquired the HTML response.

  You may search for `def EnterISML(self):` in `IgnareoG.py` for corresponding reference.

- When you are happily selecting characters......

  Your browser POST a **canvas fingerprint** to the server. This is an `MD5` string which is almost unique for everyone's computer and browser, used to prevent votes from a same device. 

  We are just to generate a random fingerprint and post it. 

  ``````python
  requests.post('https://www.internationalsaimoe.com/security', data={"secure":self.fingerprint})
  ``````

  Refer to `def PostFingerprint(self):` in IgnareoG.py.

- CAPTCHA

  We are to recognize the letters and numbers in the captcha image. We can get the image with 

  ``````python
  r = requests.get('https://www.internationalsaimoe.com/captcha/%s/%s' % (self.voting_token, int(time.time() * 1000)))
  ``````

  With `r.content` as the image, we are to POST this image to out captcha server (`captchaServer.py`), which recognize the image. My methods cannot ensure that every character in the image can be recognized (because character detection is implemented with not deep learning but traditional computer vision techniques), so **we may download multiple captcha images from the server**.

  Refer to `def AIDeCaptcha(self):` in IgnareoG.py for this part.

- Submitting your vote

  Now we are to POST your selected characters, along with the voting_token and the captcha recognition result. 

  Here I am **not** going to introduce how to generate the data to be posted. It was just some simple but tedious work implemented with `charaSelector.py` that defines which character at what probability to vote for. Civil users may ignore the details in `charaSelector.py`. 

  Military voters can debug `charaSelector.py` using the sample webpage (`.htm` file). Make sure you do understand the structure of the webpage and my codes. <u>**You should always edit your `charaSelector.py` and check it very carefully for each match.**</u> Note that **<u>you are never guaranteed to win even if you cast billions of correct votes, because ISML operators select the winner mostly according to their own preference</u>**.

  ``````python
  requests.post("https://www.internationalsaimoe.com/voting/submit",data=the_data_generated_by_you)
  ``````

  Refer to `def Submit(self):` in IgnareoG.py.

- Save your records!

  Through an ordinary manual vote, you can see a record after you submit your vote. 

  ``````python
  r = session.get('http://www.internationalsaimoe.com/voting')
  ``````

  You should GET the webpage with your **cookies**. See the official documents of `requests` to learn about `session`. An individual session is used for every simulated voter in Ignareo.

  Now you can save the record `r.text` for fun, or save billions of records and drop them at your opponents' campsite for military menace (lol). 

The whole process stated above can be run by `def Vote(self):` in IgnareoG. **You just need to write the logics to cast a single vote without having to care about concurrency, and the architecture of Ignareo can help you handle large amounts of concurrent HTTP I/O tasks.** 

## Extended features:

- Ignareo does lack convenient features, but can make use of most ready-made wheels safely.

- Retrying middleware implemented as decorators:

  `./DestroyerIGN/retryapi.py` serves as an example depicting how to implement middlewares with decoreators. Use a decorator like this:

  ``````python
  @retry(exceptions=RequestExceptions,tries=2,logger=None)
  ``````

- **Client-side** load balancing:

  Search for `csGen` in `IgnareoG.py`. To avoid any captcha server to get overwhelmed, Ignareo posts the captcha image to a different captcha server each time. Usually load balancing is implemented at the server side, but in my codes, this is achieved **only at the client side**. 

## Architecture of Ignareo

The whole voting system is of a **broker architecture**. 3 **aspects (切面)** (obtaining IP addresses, voting and captcha recognition) (You may have heard of aspect oriented programming, AOP) are **distributed in 3 types of nodes** (`Ammunition.py`, `IgnareoG.py`, `captchaServer.py`). The broker architecture has been proved to be somewhat a simple but effective, and thus popular pattern. You may refer to a well-known open standard called **Common Object Request Broker Architecture (CORBA)**, which has provided many guides for creating a standardized application. ~~Well, I did not read those guides at all when I built Ignareo.~~

IgnareoA/G is **an asynchronous HTTP server** which listens to POST from `ammunition.py`. These POSTs carry IP addresses which are used as proxies in voting. **The event loop in the Ignareo server is also used for sending asynchronous HTTP requests** to ISML.

**You can certainly run multiple processes of Ignareo** by changing `portList` in Ammunition.py, IgnareoA/G.py and captchaServer.py. You may **recognize Ignareo and its captcha servers as an elastic microservices instead of a single heavy spider application**. Control your task flow with `ammunition.py`.

**You should tell the client where the servers are.** That is, you should change the value of `captchaServers` in IgnareoG.py if you launched more captcha servers, and change `serverList` in `ammunition.py` if you deployed more Ignareo processes. 

Note that you can write all kinds of blocking codes in IgnareoG. `gevent` even turns `time.sleep()` into non-blocking pause. That means you can boast high performance automatically. But non-socket time-consuming codes (computation or long-playing HDD I/O) should be transfered to other processes.  

To control the network I/O process of IgnareoA, write your own codes in **Voter.py**.  

To change which characters to vote for, modify **charaSelector.py**.  

To tackle Cloudflare IUAM firewall (Checking your browser before…) with IgnareoA, try to extract the JavaScript carefully, using **aiocfscrape.py**. The original version offered by https://github.com/pavlodvornikov/aiocfscrape is disabled since Cloudflare changes the firewall very often. You may refer to all the resources from Github to bypass the firewall. Breaking the firewall with browsers (without exhausting reverse engineering) at high performance is also a potential research orientation.

**The trendy architecture of Ignareo has been fully tested in real combats. Just trust her as your reliable partner!**   

##  I/O engines:  

IgnareoG uses `gevent` making your `socket` asynchronous. It means you can feed gevent with multi-thread web spider codes (typically `requests`) and enjoy asynchronous performance. In principle you can even connect to databases asynchronously. The event loop of gevent on different platforms is documented at http://www.gevent.org/loop_impls.html. According to the page, **Windows users have libuv, which is likely to outperform Linux thanks to IOCP.**

IgnareoA uses the classical Python library `asyncio`. The codes in IgnareoA have to be literally asynchronous with `async def`, `ensure_future`, `await` and  `add_callback`.  

To summarize, **you can just use Ignareo with low-level APIs provided by asyncio or gevent**. The event loop is running forever in the server.

You may also have a try with ```trio``` or ```httpx```. I have not implemented such a version, so help yourself and happy coding!  

## A generic code structure for civil users

Referring to IGN, your web spider can be fabricated conceptually with 3 cascades:  

1. task producer
2. -> main network I/O
3. -> servers for computation-intensive tasks

Every later cascade is an http server for the previous one. 

- The task producer collects, neatens and gives the necessary information to start new tasks. In my application it refers to `Ammunition.py`  which collects proxies from the Internet.

  In the early stages of developing the spider we may, **by instinct**, ask each worker thread to obtain 1 proxy for its own use. This has been proved to be **inefficient** in our practice when large numbers of worker threads with complicated logics are launched. **Workers should be launched passively corresponding to generated tasks. Proxies had better be loaded actively by an external process. Otherwise there can be heavy coupling and a bottleneck of performance.**  

  Sometimes you may need multiple types of information to start a task (e.g. a cookie and a proxy). In such cases I suggest building separate task producers for different types of necessary information. 

- The main network I/O cascade should execute the tasks like Ignareo does. If multiple types of information is necessary for a task, you may need an integrated task queue or even a lightweight database in Ignareo. Classical messaging queues like RocketMQ, RabbitMQ or even redis are also possible alternatives, but they do make the whole system heavier. Since you are running HTTP-oriented tasks, **you could have got everything done with HTTP**.

- **Computation-intensive tasks should be extracted from the main I/O engine.** This is to avoid running out of memory and CPU single-core capability too quickly. **Running out of CPU in a single Python network I/O process may cause bunches unhandled HTTP responses to pile up.** That's also a reason why I use 10 processes of IgnareoG to decrease the average load of each process.

  Actually I have assembled a web spider system named `Valgulious` for ISML, which has a captcha recognition system in each process of spider. This has been proved to be overwhelmingly heavy for most personal computers in combats. In the later version named `Seniorious` I extracted the captcha module as a discrete service, which marked the first giant leap in building the ISML auto voter as microservices.

This 3-cascade paradigm provides an example involving all kinds of HTTP I/O and computation. All the processes can be easily distributed on different machines.  

**Hopefully Ignareo serves just as a concept** of high performance HTTP I/O engine, rather than a heavy framework. **I tried to make no decision for you**, except for performance and convenience of transplanting your other web spiders.  

## Why Ignareo instead of Scrapy?  

I have already developed an auto voter in 2018, using Scrapy. Scrapy is truly a great framework.  

The first reason why I aborted Scrapy is that it can cause critical trouble when you need a non-blocking pause between two requests. It seems you have to set the pause before receiving the response of the first request (https://stackoverflow.com/questions/36984696/scrapy-non-blocking-pause). Consequently it becomes difficult to control the interval of requests.  

Secondly, Scrapy probably does not maintain synced(connected?) with the server. It starts another TCP connection with new SYN for every new request. This characteristic not only leads to redundant SYN flow, but also makes it easier for the website to detect the spider. For example, Scrapy may start a new TCP connection sending a POST request. Real browsers never do so!  

Last but not least, the codes for a Scrapy spider, crammed in a single class and ran in a single process, can be chaotic and frustrating to understand and maintain.  

It's very difficult to predict or control the detailed behavior of Scrapy, because it is such a great framework, making most decisions for you, hiding most of its source codes. This is good in many cases, but when you execute your personalized demands and decisions, you have to fight the framework.  

Destroyer Ignareo, as a reinvented wheel, is re-designed for the future. With only hundreds of lines of codes in the core, she allows you to define your own work flow, and understand everything about her. Now you can focus more on data parsing and dependency.  

## Brief introduction for ISML voters:  

Screaming high concurrency! Light weight Convolutional Neural Network! Against captcha within 0.06 seconds per image on CPU! 
Easy for distributed deployment!  

The structure of IGN can be applied for any saimoe voting and even more in principle (I'm using IgnareoA to monitor IoT devices). Using IGN for other purposes is also welcomed. **Feel free to raise** ***Issues*** **including "我永远喜欢珂朵莉", "I love Chtholly forever", "私はいつまでもクトリが好きです", and even more!** （请扭曲的珂学家不要一夜之间刷两千条……）  
However, **BE CAREFUL in case your operations may result in a CC attack!** (I've killed an SQL service imprudently with IGN...)  

## How do I build Ignareo?  

By reading documents of many (possibly) useful libraries!  

## Miscellaneous logs

June 7, 2020: No warranty for ISML 2020. No possibility for darkest horses to win.    

Apr. 13th, 2020: Long time no see!  
To developers who want to integrate more services (e.g. selenium browser cluster) with Ignareo:  
Ignareo can be "Cloud Native". Docker-compose and Kubernetes may help you manage millions of machines running billions of services.  

Mar. 21st, 2020:  
An image library of Sukasuka/Sukamoka:  
https://img.sukasuka.cn/  
Using:  
https://github.com/rr-/szurubooru  

And wiki:  
https://wiki.sukasuka.cn/  

Oct. 12th, 2019: *Ignareo.py* will be **renamed** as ***IgnareoA.py***. **The name *Ignareo* now refers to the whole series of programs (the whole project)**  

Sep. 13th, 2019: >asyncio.ensure_future(self._post('httpc://chtholly.68',data=r'祝妖精仓库中秋快乐！'.encode('月饼')))  

July 19th, 2019: **[Strongly Recommended]** Welcome to the novel (under GPL-3.0 license) at /DestroyerIGN/CINT the Space Fleet Hecate2  
欢迎阅读DestroyerIGN附赠的小说！(按GPL-3.0开源协议发布)  
https://github.com/Hecate2/ISML_auto_voter/raw/master/DestroyerIGN/CINT%20the%20Space%20Fleet%20Hecate2%20(%E6%9C%AA%E9%85%8D%E4%B9%90).docx  
**For more information: log.md**

## Tips! What if ISML responds very slowly?  
First, please allow me to ascribe the reason dogmatically to spammers using pristine selenium wildly.  
By running a miniature version of stress test involving a mixture of selenium, multi-thread spamming programs and IGN, I would like to give the following suggestion:
> **STOP USING IGN** when ISML is really slow. If you persist reloading IGN with ammunition very quickly, it can be extremely difficult for everyone (both humans and programs) to submit vote. **Neither bots nor humans will be able to submit**! Therefore,  ISML would receive very few votes for hours, until someone quit.  

**But why?**  
Well, selenium and multi-thread web spiders has a ***limited*** number of "**workers**" (the word may refer to either processes, threads or coroutines), but the number of workers of IGN is ***almost unlimited***. The jobs launched by workers but not responded by servers are usually kept in the program, waiting. 
Exerting pressure on a server with limited "workers" can hardly lead to a Denial of Service, because they do not start new spamming attempts when all the workers have to wait. So most of the workers can receive their responses sooner or later. But IGN doesn't care about slow responses and keep raising more attempts. With the passage of time (perhaps within only a few minutes in actual battles), it is likely that IGN would own the absolute major portion of unresponded requests, which will be far more than what ISML can handle. The increase of unresponded requests, however, gives even more positive feedback to generating unhandled spamming attempts, since IGN does not care about the unresponded ones! Only the timeout and the failure of proxies can stop IGN from holding more requests.  
> And do not assume yourself as the undisputed winner when you take up all the hardware resources of ISML with your ancient spamming programs. You can't exclude IGN at all, but you rile everyone.  

## Tips! Important for the most wealthy voters!
As the saying goes: *Victorque has hundreds of thousands of bilibili accounts*.  
**Before you challenge a rich supporting group, you should always consider such a probable fact: though IGN can support 2500 to 5000 voters on your computer, your opponent has hundreds of machines, each can run 25 to 50 selenium browsers. Meanwhile, you can't afford the cost for proxies.**   

0. Spamming **TOO MANY** votes is usually meaningless, except for burning your own $dollars, making difficulties for ISML operators, and delaying the following matches.  
1. Think before you cast billions of votes in a few minutes. If you really would like to spam, spread your votes to the whole 24 hours. Quick spamming are sure to be recognized by ISML operators.  
2. Think twice if you want to challenge any character. You should disguise yourself very well, and you know you may get revenged.  
3. ~~Think three times if you want to vote billions against the wish of ISML operators.~~ The justical operators have the right to ignore your votes without certain proof!  
4. Think four times if you want to challenge some super-rich supporting groups. The cost for employing programmers is just a piece of cake for them, since they have hundreds of thousands of budget for all kinds of saimoe platforms! Well, that is not at all a large sum of money if everyone burns cash with IGN, but you should always assume that they have infinite wealth.
5. Think five times before you launch IGN, because IGN drains everyone's life and wealth. You are a human, not a leprechaun! 
6. IGN is designed to create a nuclear balance and deprive the monopoly of some evil supporting groups. I don't mind your bombing them with IGN, but please **VOTE BY HAND**, and **DON'T spam irresponsibly with IGN** if you really intend to support me! Nobody gains real happiness through a nuclear war! If you really have to spam against the evil, think about all the factors carefully.  
7. ~~Vote **(by hand!)**~~ **Invest your billions of ¥, ￥, $, €, ￡,… in a 2nd season of anime** for Chtholly Nota Seniorious if you really love her!  
8. 有钱请捐给世萌，不要捐给代理ip供应商或者大厨。Donate your billions of dollars to ISML instead of proxy suppliers! Never buy a spamming service from rich supporting groups!  

Remember that: Nobody is with almighty justice. Nobody sees the end of war until death.  

Again: Thank you very much for fighting against all the bad sides in all kinds of saimoes!  

## Accessories: 

**ISMLnextGen**, which contains some prototypes and basic code blocks, is the lab for the development of IGN.  

## Acknowledgements

First of all, please allow me to extend my sincerest gratitude to  

<font color=#0099ff>Chtholly Nota Seniorious</font>,  

Tiat Siba Ignareo,  

Ithea Myse Valgulious,  

Nephren Ruq Insania,  

and  

<font color=DodgerBlue>Shino Asada</font>,  

who always charge my will to conquer all the difficulties.  

Thanks to Lilya Aspray the Legal Brave, and all the leprechauns (including all that live in the past or future) from SukaSuka/SukaMoka series. 

Thanks to all humans that support Ignareo, including but not limited to the contributors of all the magnificent open codes utilized by Ignareo. 

Thanks to my supporting group, which invested huge funds to give birth to the previous generations of auto voter programs.
Thanks for their trust and cultivation on me.  

Thanks to ISML, as well as other saimoe platforms, 
which gives me the opportunity and an arena to practice web spiders and other technologies. 
Perhaps saimoe tournaments in the future should give up deciding who is the most moe character, and focus more on training programmers.  

Thanks to some of my opponents in saimoe, who developed brilliant programs to inspire and spur on me.  

Thanks to all the ***Chthollists*** who love Chtholly and SukaSuka.  
