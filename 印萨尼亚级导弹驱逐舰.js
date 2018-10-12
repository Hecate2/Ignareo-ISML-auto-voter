// ==UserScript==
// @name         Insania class destroyer
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       Hecate2
// @match        https://www.internationalsaimoe.com/voting
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    //这是JavaScript不是cpp
    //自动点击角色为其投票的代码：
    var chara=	//如果只修改外交，不修改程序，只需看var chara这部分 
    {
	    //首先是非顺位赛（点击直接选中，无需给数字的比赛）
	    //下面设置必须要投的角色，以及投她/他/它的概率
	    //可以把某角色的概率设得很低，保证很少投她/他/它
	    //设为负数保证不投她/他/它
        "select":
		[
			["Asada Shino",2.0],
			//角色名，以及保证选中她/他/它的概率
            //大于1的概率保证选中，小于0的概率保证不选
            //可以设置很小的概率来拒绝给某个角色投票
            //会用角色名在"角色名\n\n作品名"中试图匹配
            //因此在角色名不易混淆的时候不用填"\n\n作品名"
            //如果select中有两个角色直接对决，则写在前面的角色优先被选
			//字典中两个角色直接对决时，若要写在后面的角色被选
			//则要求后面的角色按概率被选，且前面的角色按概率没有被选 
            //注意不要忘记右方括号后面的逗号
            ["Chtholly Nota Seniorious",2.0],
            ["Willem Kmetsch",2.0],
            ["Gilgamesh",0.9],
            ["Haibara",0.6],
            ["Kurisu",0.7],
            ["Izumi Sagiri",0.6],
            ["Hikigaya Hachiman",0.85],
            ["Uiharu Kazari",2.0],//test!
            ["Shokuh",2.0],//test!
        ],
		//然后是需要给数字的比赛 
		//根据世萌比赛规则，给的数字越小越支持该角色
		//只要所有你不想支持的角色的数字大于所有想支持的角色的数字 
		//则你对不想支持的角色的不支持力度等同于给她abstain?
		//当然你可以给某角色暴投abstain，但这对程序性能没好处 
		"rank":
		[
			["Chtholly Nota Seniorious",1,2.0,2],
			//角色名，愿意给出的最小数字，确实给这个数字的概率，愿意给的最大数字 
			//数字越小越支持！
			//给出的数字为0表示填abstain 
			//如果你愿意给出的最小数字比角色的个数还大，我就给随机数(含abstain)
			["Asada Shino",1,2.0,2],
			//["某个想暴投abstain的角色",0,2.0,0],
			//如果rank中有两个角色直接对决，且要求给出相同的非0数字
			//则rank中排在前面的优先被给数字 
			//特别注意:
			//如果因冲突或按概率没有给某个角色最小数，则试图给这个角色一个逐渐递增的数
			//任何时候如果逐渐递增的数超出了愿意给出的最大数字，则这个角色会被给随机数字！！  
			//一种例子是有3个rank里的角色直接对决，每个3色都要求被给1或2
			//则最后的倒霉鬼会被给出不是1不是2的随机数字
			
			//推荐设置为：rank中第i个角色愿意给出的最大数字为i，最小数字为1 
		],
    }
    //var chara结束。只修改外交者无需看下面
	
	var reset=document.getElementById("voting_form_reset");
	reset.click();
	
	var i,j,k,tmp;//循环变量和临时变量 
	var charaTable=[];//给数字的比赛中，还有哪些角色没给数字 
	var valueTable=[];//给数字的比赛中，还有哪些数字没给出 
	var tmpRank=[];//把chara.rank复制一份暂存进tmpRank[] 
	var tmpRankTable=[];//记录tmpRank中每个在arena里的角色在arena中的哪个下标 
	var allowed=0;//用于流程控制的变量，功能很多 
	var rand=0.0;//记录一个随机数 
	var selectDensity=Math.sqrt(Math.sqrt(Math.random()*Math.random())/2.0+0.5);
	//决定不用给数字的比赛的选择密度，取值范围根号(0.5)到1 
	//根号(根号(0到1随机数×0到1随机数)/2+0.5)
	//每次投票都会有不同的选择密度！ 
	var selectRate=Math.random()*Math.random()/8.0+7.0/8.0;
	//给数字的比赛中给一个新数字的概率，取值范围7/8到1 
	//如果有一次按概率没给新数字，则直接退出，再也不给新的数字了
	
	//下面的function求substr在str中出现的次数
	//CapIgnore为True时忽略大小写，为False时检查大小写 
    function countSubstr(substr, str, CapIgnore)
	{
	    //var count;
	    //var reg = "";
	    if (CapIgnore == true)
		{
	        //reg = "/" + substr + "/gi";
	        substr = "/" + substr + "/gi";
	    }
		else
		{
	        //reg = "/" + substr + "/g";
	        substr = "/" + substr + "/g";
	    }
	    //reg = eval(reg);
	    substr=eval(substr);
	    if (str.match(substr) == null)
		{
	        //count = 0;
	        return 0;
	    }
		else
		{
	        //count = str.match(reg).length;
	        return str.match(substr).length;
	    }
	    //return count;
	}
	//一个"standard_voting_arena"里面存在的abstain个数如果大于1
	//则是多个角色，需要给数字的比赛。abstain个数减1即为角色个数 
	
	//下面的function从一维列表arr中移除一个值为val的元素，且列表长度会被减1，不会留空位 
	function removeByValue(arr, val)
	{
		for(var i=0; i<arr.length; i++)
		{
			if(arr[i] == val)
			{
				arr.splice(i, 1);
				return true;
			}
		}
		return false;
	}

	//下面的function生成min到max的随机整数，包含min和max 
	function ranInt(min,max)
	{
		if(min>max)
		{//交换两个数的值 
			min=min+max;
			max=min-max;
			min=min-max;
		}
		return Math.floor(Math.random()*(max-min+1)+min);
	}
	
    //var abstain=document.getElementsByClassName("voting_abstain_btn")
    //获取所有abstain按钮

    //var box=document.getElementsByClassName("voting_standard_contestant_content");
    //box获得所有角色按钮
	
	//预处理：删除chara.rank里的异常输入
	for(i=0;i<chara.rank.length;++i)
	{
		if(chara.rank[i][1]>chara.rank[i][3])
		{
			removeByValue(chara.rank, chara.rank[i]);
		}
	} 
	
    var arena=document.getElementsByClassName("standard_voting_arena");
    var count=0;//统计每个arena有几个abstain  

	//暴力click()点击会降低浏览器性能，所以我们尽量不做无意义点击 

    for (i=0; i<arena.length; ++i)	//对于每个arena
    {
		allowed=0;//设为默认值保平安 
		count=countSubstr("Abstain", arena[i].innerText, true);
		//在arena里找abstain的个数，忽略大小写 
		if(count==1)
		//整个arena只有1个abstain，是两者选一，无需给数字的比赛 
		//此时点击arena[i].children[5]和arena[i].children[6]即可选角色
		//而点击arena[i].children[7]即是abstain 
		{
	        for (j=chara.select.length-1; j>=0; --j)
			//从后往前翻select字典，看children[5]的角色是否出现在字典中 
	        {
	            if(arena[i].children[5].innerText.indexOf(chara.select[j][0])>-1
			 && Math.random()<chara.select[j][1])
	            //如果children[5]在字典里查到了，则以字典设定的概率允许点击children[5]
	            {
	                //arena[i].children[7].click();	//点击abstain保平安
					//arena[i].children[5].click();
	                allowed=5;//允许点击children[5] 
	                break;
	            }
	        }
			//下面从后往前翻select字典，看children[6]的角色是否出现在字典中
			//但字典里优先级比children[5]还低的就不翻了 
	        for ( ; j>=0; --j)
	        {
			    if(arena[i].children[6].innerText.indexOf(chara.select[j][0])>-1
			 && Math.random()<chara.select[j][1])
	            //如果children[6]在字典里查到了，且优先级比children[5]高
				//则以字典设定的概率允许点击children[6]
	            {
	                //arena[i].children[7].click();	//点击abstain保平安 
					//arena[i].children[6].click();
	                allowed=6;
	                break;
	            }
	        }
	        if(allowed==5 || allowed==6)	//如果这个二选一arena里有字典内的角色 
	        {
	        	//arena[i].children[7].click();	//点击abstain保平安
	        	arena[i].children[allowed].click();
		        allowed=0;//不许再随机点击这个arena 
			}
			else
			{
				allowed=1;//允许随机点击这个arena 
			}
			if(allowed==1)
			{//随机点击这个arena 
				rand=Math.random();
				if(rand<selectDensity/2.0)
				{
					arena[i].children[5].click();
				}
				else if(rand<selectDensity)
				{
					arena[i].children[6].click();
				}
			}
    	}
    	else//不止一个abstain，说明这是给数字的比赛
		//arena里的角色个数为abstain个数减1，也就是count-1
		//arena里角色的下标为5到count+4 
    	{
    		count=count-1;	//count减1后就是arena里的角色个数 
			charaTable=[];
			valueTable=[];
			for(j=0;j<count;++j)//预处理：初始化查找表 
			{
				charaTable[j]=j+5;//每个角色都没给过数字 
				valueTable[j]=j+1;//每个数字都没给过 
			}
			tmpRank=[];
			for(j=0;j<chara.rank.length;++j)
			{
				tmpRank[j]=chara.rank[j];//复制chara.rank到tmpRank 
			}
			tmpRankTable=[];
			for(j=0;j<tmpRank.length;++j)
			//预处理：删除tmpRank里没出现在arena里的角色 
			//删除chara.rank里出现在arena里的角色 
			//记录tmpRank里出现在arena里的角色具体出现在arena里哪个下标 
			{
				tmp=false;
				for(k=5;k<count+4;++k)
				{
					if(arena[i].children[k].innerText.indexOf(tmpRank[j][0])>-1)
					{
						tmp=true;//tmpRank[k]出现在了arena 
						break;
					}
				}
				if(tmp==true)//tmpRank[j]出现在了arena
				{
					removeByValue(chara.rank,tmpRank[j]); 
					tmpRankTable[j]=k;//记录arena里的下标 
				}
			}
			for(j=0;j<tmpRank.length; )
			{
				if(typeof(tmpRankTable[j])=="undefined")
				{
					tmpRank.splice(j, 1);
					tmpRankTable.splice(j, 1);
				}
				else
				{
					++j;
				}
			}
			
			//开始给数字！ 
			while(tmpRank.length>0)
			{
				if(Math.random()<tmpRank[0][2])//按概率给数字成功 
				{
					if(tmpRank[0][1]==0)
					{
						arena[i].children[tmpRankTable[0]].firstElementChild.lastElementChild.value=0;
						removeByValue(charaTable,tmpRankTable[0]);
						removeByValue(tmpRank,tmpRank[0]);
						removeByValue(tmpRankTable,tmpRankTable[0]);
					}
					else if(removeByValue(valueTable,tmpRank[0][1]))//删除数字表里的这个数字成功 
					{
						//给数字 
						arena[i].children[tmpRankTable[0]].firstElementChild.lastElementChild.value=tmpRank[0][1];
						//删除tmpRank[0]和tmpRankTable[0] 
						removeByValue(charaTable,tmpRankTable[0]);
						//removeByValue(valueTable,tmpRank[0][1]);
						removeByValue(tmpRank,tmpRank[0]);
						removeByValue(tmpRankTable,tmpRankTable[0]);
					}
					else
					{
						tmpRank[0][1]+=1;
					}
				}
				else if(tmpRank[0][1]==0)
				{
					removeByValue(tmpRank,tmpRank[0]);
					removeByValue(tmpRankTable,tmpRankTable[0]);
				}
				else
				{
					tmpRank[0][1]+=1;
				}
				
				if(tmpRank.length>0)
				{
					if(tmpRank[0][1]==tmpRank[0][3])//希望的最小值已经等于允许的最大值 
					//会出错，但可以继续执行 
					{
						tmpRank[0][2]=2.0;//下一次必须给出值 
					}
					else if(tmpRank[0][1]>tmpRank[0][3] || tmpRank[0][1]>count)
					//希望的最小值已经大于允许的最大值，或者大于角色总数 
					{
						removeByValue(tmpRank,tmpRank[0]);//删除tmpRank[0]
					}
				}
			}//字典里要求给的数字已经给完
			//开始给arena里剩下的角色发数字，至少选4个 
			while(charaTable.length>0)
			{
				if(valueTable[0]<=4 || Math.random()<selectRate)
				{
					rand=charaTable[ranInt(0,charaTable.length-1)];
					arena[i].children[rand].firstElementChild.lastElementChild.value=valueTable[0];
					removeByValue(charaTable,rand);
					removeByValue(valueTable,valueTable[0]);
				}
				else
				{
					break;
				}
			}
			charaTable=[];//清空查找表 
			valueTable=[];//清空查找表 
			allowed=0;//给后面的过程做准备
		}
    }

	var selectDensity=Math.sqrt(Math.random())/2.0+0.5;
	//重新生成selectDensity，范围0.5到1 
    //最后填写性别，年龄，检查验证码，准备submit
    var gender=document.getElementsByClassName("voting_gender_input");
    //获取性别按钮
    var rand=Math.random();//随机数决定选哪个性别
    if(rand<selectDensity)
    {
        gender[0].click();//selectDensity概率男
    }
    else if(rand<0.95)
    {
        gender[1].click();//95%-selectDensity概率女
    }
    //5%概率abstain

    var age=document.getElementsByClassName("voting_age_input");
    //获取年龄按钮
    rand=Math.random();//随机数决定选哪个年龄
    if(rand<1.0-selectDensity) 
    {
        age[1].click();//1.0-selectDensity概率小于18
    }
    else if(rand<0.975)
    {
        age[0].click();//97.5%+selectDensity-1.0概率大于等于18
    }
	//2.5%概率abstain
    

    //var captchaInput=document.getElementById("captcha_input");
    //获取验证码输入框

    var submit=document.getElementById("voting_form_submit");
    //获取submit按钮
    submit.disabled=false

    //验证码使用Python在后端搞定，不使用JavaScript
    //这里JavaScript只检查验证码是否填好，不试图填验证码
    //下面准备点击submit
    //allowed=1;	//允许点击submit
    //function submitClick(allowed,submit,captchaInput)	//点击submit按钮提交投票
    //{
    //	if(allowed==1 && submit.disabled==false && captchaInput.value.length==8)
    //	//如果提交按钮可用，且验证码已输入8个字符
    //	{
    //		submit.click();
    //		//点击submit按钮（目前被注释了，不会生效）
    //		allowed=0;	//不再允许点击submit
    //		return allowed;
    //		//其实return 0就好了，不过上面两句这样写便于理解
    //	}
    //	else
    //	{
    //		allowed=1;
    //		return allowed;
    //		//其实return 1就好了，不过上面两句这样写便于理解
    //	}
    //}
    //var timer=setTimeout(alert('Submitting!'),90500+Math.floor(Math.random()*5000));
    //90.5秒+随机一段时间（最多5秒）后执行submitClick()
    //submit.click()

    // Your code here...
})();
