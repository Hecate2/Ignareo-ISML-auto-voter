# Missile Destroyer Insania (Prototype in Sept. 2018)
导弹驱逐舰印萨尼亚，2018年9月原型舰状态。

https://www.internationalsaimoe.com/voting

在下学Python到现在只有一个月。如果代码太菜太乱缺注释，还请海涵。

目前还在用Python模拟鼠标键盘进行操作。大神们能用更好的方式让它高效一点吗？

如果你是世萌运营组成员……没关系，这台机器的效率远不及单人手动刷票

世萌查伪原理（包括但可能不仅限于）：IP地址、Cookie、Canvas指纹、User Agent



使用要求：

Windows 7或10操作系统

1080P屏幕分辨率（如果不是，则需要修改鼠标点击的位置）

Python 3.6，安装好我import的包

注册一个提供ip代理的平台，把获取代理的API链接填入Python文件的proxyAPI变量。我使用的是芝麻代理。如果使用其他平台，可能需要修改解析ip地址的函数。

注册一个识别验证码的平台，把密码串填入Python文件的captchaPSWD变量。我使用的是91验证码平台。如果使用其他平台，可能识别验证码的函数都要大改。

开出512MB的内存当硬盘来用，在内存里安装火狐浏览器，设为默认浏览器，在浏览器里安装插件：

    CanvasBlocker，设置为伪造取出API
    
    Cookie AutoDelete，启用自动清理Cookie
    
    User Agent Switcher，设置为打开随机模式，“仅启动时”，勾选“桌面端”和“移动端”
    
    tampermonkey，输入我提供的JavaScript即可自动选择角色、性别、年龄。可以在JavaScript的chara里修改给各个角色投票的概率。适用于二选一和给数字的比赛。

最好把插件搬进内存里。这需要修改火狐的配置文件。



工作原理：运行Python程序，

Python自动从proxyAPI找一个代理，修改windows注册表以设置该代理

Python打开火狐浏览器，打开投票页面。启动浏览器时Cookie会被插件自动清空

tampermonkey里的JavaScript自动选好角色

一旦Python利用屏幕上的颜色认为投票页面已经打开，就滚屏到页面底部，在屏幕上用类似PrintScreen的方式截取验证码图片。

判断截得的图片是不是验证码。如果是，发给打码平台，过一会收取结果

模拟鼠标点击验证码输入框，输入验证码

点击Submit，过一会后关闭浏览器。



现存问题：

识别验证码准确率不够

鼠标键盘式的流程控制导致稳定性和效率都不佳

编译成exe文件较困难，难以推广给群众使用（要让不会装Python的群众使用，只能直接发布一台虚拟机）
