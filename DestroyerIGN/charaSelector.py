#coding:utf-8
#import json
from math import ceil
import random
import re

import AdvancedHTMLParser

def selector(html,voting_token,vcode):
    select=[#设置二选一投票。写在前面的优先被满足
        ["Chtholly",2.0],#角色，投这个角色的概率(大于等于1就是必投)
        ["Willem",2.0],
        
        #["Kanna",0.15],
        #["Hikigaya",0.21],

        #["Tōru",0.06],
        #["Illyasviel",0.02],
        #["Gilgamesh",0.03],
        #["Sakurajima",0.1],
        #["Emilia",0.05],
        #["Makise",0.06],#助手的对手是纱雾
        #["Izumi Sagiri",0.06],
        #["Alice",0.08],
        #["Prohibitorum",0.05],#茵蒂克丝
        
        #["Minamoto Sakura",0.254],#源樱，佐贺偶像是传奇
        #["Zero Two",0.524],
        #["Takasu Ryūji",0.05],
        #["Tachibana",0.041],#立花泷                       
        #["Izawa",0.1],#井泽静江                         
        #["Misaka",2.0],                                                 
        #["Pikachu",0.5],                                   
        #["Alice Zuberg",0.05],
        #["Minamoto Momo",0.162],#源桃，月影特工，反击樱岛麻衣
        #["Futaba Rio",0.035],
        #["Yoroizuka Mizore",0.044],#铠冢霙
        #["Megumin",0.05],
        #["Rikka",2.0],
        #["Kanna",0.8],
        #["Rinne",0.5],
    ]
    rank=[#设置给数字的投票
        #rank记录的是一条一条规则。程序会先随机发数字，然后尝试满足每条规则。
        #写在前面的规则绝对优先被满足。为此可以任意牺牲后面的规则
        [1,"Willem","Togashi","Todoroki"],
        #[n,角色名，角色名，更多角色名……]
        #保证这个列表中前n个角色的数字严格比后面剩余所有角色的数字更好
        #而前n个角色内部，比较有可能是放在前面的比放在后面的好，但精确概率难以计算
        #[1,"Makise","Shiro","Kanna"], 
        #["Willem",1,0.7,7],
        #["Kurisu",1,0.15,7],
        #["Illya",4,0.066967,10],
        #["Willem",1,0.5,2],
        #["Gilgamesh",5,0.5,6],#角色名，愿意给的最好数字，概率，愿意给的最差数字
        #["Willem",1,0.5,3],
        #["Kurisu",1,0.5,3],
    ]
    
    #selectDensity=random.random()*random.random()/3.0+0.7  #二选一的选择密度
    selectDensity=0.75
    #selectRate=random.random()*random.random()/5.0+4.0/5.0 #给一个新数字的概率
    selectRate=0.87
    
    #parser = AdvancedHTMLParser.AdvancedHTMLParser(filename="ISML 2018 Ruby Necklace.htm", encoding='utf-8')
    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(html)
    #("ISML 2018 Ruby Necklace.htm")
    #Tag=AdvancedHTMLParser.AdvancedTag()
    
    data={
        'voting_token': voting_token,'captcha_token': '','timelimit': '90',
    }
    
    arena=parser.getElementsByClassName("standard_voting_arena")
    i=0
    #for arena in arenas:
    while(i<len(arena)):
        arenaToken=re.search(r"[0-9]\d*",arena[i].innerHTML).group()
        count=int(re.findall(r'[0-9]\d*',arena[i].outerHTML)[5])
        #print(count)
        if(count==1):#二选一arena
            data['min['+arenaToken+']']='1'
            data['arena_num['+arenaToken+']']=arenaToken
            data['max['+arenaToken+']']='1'
            data['arena_token['+arenaToken+']']=arenaToken

            allowed=0
            j=0
            while(j<len(select)):
                if(arena[i].children[5].textContent.find(select[j][0])>-1 and random.random()<select[j][1]):
                    #按字典中的概率投票
                    data['contestant['+arenaToken+'][0]']='0'
                    data['contestant_vote['+arenaToken+'][0]']='1'
                    data['contestant['+arenaToken+'][1]']='0'
                    data['contestant_vote['+arenaToken+'][1]']='0'
                    allowed=5
                    break
                j+=1
            j-=1
            while(j>=0):
                if(arena[i].children[6].textContent.find(select[j][0])>-1 and random.random()<select[j][1]):
                    #按字典中的概率投票
                    data['contestant['+arenaToken+'][0]']='0'
                    data['contestant_vote['+arenaToken+'][0]']='0'
                    data['contestant['+arenaToken+'][1]']='0'
                    data['contestant_vote['+arenaToken+'][1]']='1'
                    allowed=6
                    break
                j-=1
            if(allowed!=5 and allowed!=6):
                #随机投这个arena
                rand=random.random()
                if(rand<selectDensity/2.0):
                    data['contestant['+arenaToken+'][0]']='0'
                    data['contestant_vote['+arenaToken+'][0]']='1'
                    data['contestant['+arenaToken+'][1]']='0'
                    data['contestant_vote['+arenaToken+'][1]']='0'
                elif(rand<selectDensity):
                    data['contestant['+arenaToken+'][0]']='0'
                    data['contestant_vote['+arenaToken+'][0]']='0'
                    data['contestant['+arenaToken+'][1]']='0'
                    data['contestant_vote['+arenaToken+'][1]']='1'
                else:
                    data['contestant['+arenaToken+'][0]']='0'
                    data['contestant_vote['+arenaToken+'][0]']='0'
                    data['contestant['+arenaToken+'][1]']='0'
                    data['contestant_vote['+arenaToken+'][1]']='0'
        elif(count==12):#单个角色给0到10分的赛制
            data['min['+arenaToken+']']='1'
            data['arena_num['+arenaToken+']']=arenaToken
            data['max['+arenaToken+']']='12'
            data['arena_token['+arenaToken+']']=arenaToken            

            j=0
            while(j<count):#遍历arena
                allowed=1#允许给随机数字
                k=len(rank)-1
                while(k>=0):
                    if('str' in str(type(rank[k][0])) and arena[i].children[j+5].textContent.find(rank[k][0])>-1):
                        value=rank[k][1]
                        while(random.random()>rank[k][2] and value<=rank[k][3] and value<=8):
                            value+=1
                        value+=0.1*random.randint(1,9)
                        if (random.random()<0.3):
                            value=ceil(value)
                        value=round(value,2)
                        data['contestant['+arenaToken+']['+str(j)+']']='0'
                        data['contestant_vote['+arenaToken+']['+str(j)+']']=str(value)
                        #print(str(value))
                        allowed=0#不许给随机数字
                        rank.pop(k)
                        break
                    else:
                        k-=1
                if(allowed==1):
                    if(random.random()>selectRate):
                        value=0
                    else:
                        value=random.randint(0,5)+random.randint(0,4)+0.1*random.randint(1,9)
                        if (random.random()<0.1):
                            value=round(value)
                        value=round(value,2)
                    #print(value)
                    data['contestant['+arenaToken+']['+str(j)+']']='0'
                    data['contestant_vote['+arenaToken+']['+str(j)+']']=str(value)
                j+=1
        else:#给数字arena
            data['min['+arenaToken+']']=str(count)
            data['arena_num['+arenaToken+']']=arenaToken
            data['max['+arenaToken+']']=str(count)
            data['arena_token['+arenaToken+']']=arenaToken

            #valueTable=[n for n in range(1,count+1)]   #还有哪些数字没给
            #0(Abstain)是可以无限给的，所以不放在valueTable
            charaTable=[arena[i].children[n].textContent for n in range(5,count+5)]
            charaIndexTable=[n for n in range(0,count)] #哪些下标的角色还没给数字
            charaValueTable=[0 for n in range(0,count)] #每个角色当前被给的数字
            #count-=1    #现在count是角色个数-1
            #不执行上一句。count等于角色个数
            
            #先随便发数字。找一个随机角色，给他发1，再找一个随机角色，给他发2...
            value=1
            while(value<=count and random.random()<selectRate):
                rand=random.randint(0,len(charaIndexTable)-1)
                charaValueTable[charaIndexTable[rand]]=value
                charaIndexTable.pop(rand)
                value+=1
            maxValue=value-1#记录已经给出的最大数字
            
            #然后遍历rank
            k=len(rank)-1
            while(k>=0):
                if('str' in str(type(rank[k][0]))):#首个元素是字符串，即给某角色指定数字范围
                    if(rank[k][1]>count or rank[k][1]>rank[k][3]):
                        rank.pop(k)
                    else:
                        j=0
                        while(j<count):#遍历arena
                            if(charaTable[j].find(rank[k][0])>-1#如果rank里这个角色在arena里存在
                               and (charaValueTable[j]<rank[k][1] or charaValueTable[j]>rank[k][3])):
                                #找个可给的数字
                                value=rank[k][1]
                                while(random.random()>rank[k][2] and value<rank[k][3] and value<count):
                                    value+=1
                                if(value>maxValue):
                                    #打算给的数字大于已给的最大数字。此时不仅要给出数字，还要把中间跳过的数字也补足
                                    #而且如果这个角色原本被给过数字，则原本被给的数字也要补出来
                                    tmp=0
                                    if(charaValueTable[j]!=0):#这个角色被给过数字了
                                        tmp=charaValueTable[j]#记录下来
                                    else:
                                        charaIndexTable.remove(j)#设定这个角色被给过数字了
                                    #先给数字
                                    charaValueTable[j]=value
                                    #给数字完毕。下面补出跳过的数字
                                    #先补出该角色原来的数字
                                    if(tmp!=0):
                                        rand=random.randint(0,len(charaIndexTable)-1)
                                        charaValueTable[charaIndexTable[rand]]=tmp
                                        charaIndexTable.pop(rand)                                                                                
                                    #再补出该角色现在的数字与maxValue之间所有的数字
                                    maxValue+=1
                                    while(maxValue<value):
                                        rand=random.randint(0,len(charaIndexTable)-1)
                                        charaValueTable[charaIndexTable[rand]]=maxValue
                                        charaIndexTable.pop(rand)                                        
                                        maxValue+=1
                                    maxValue=value
                                else:
                                    #打算给的数字小于等于已给的最大数字。此时直接给的话会和别的角色数字重复。应与另一角色交换数字
                                    if(charaValueTable[j]==0):
                                        charaIndexTable.remove(j)
                                        maxValue+=1
                                        charaValueTable[j]=maxValue
                                    tmp=charaValueTable.index(value)
                                    charaValueTable[j],charaValueTable[tmp]=charaValueTable[tmp],charaValueTable[j]
                                rank.pop(k)
                                break
                            else:
                                j+=1
                elif('int' in str(type(rank[k][0]))):#首个元素是整数，即指定某些角色排在另一些角色前面
                    rank[k][0]=min(rank[k][0],len(rank[k])-1)
                    #先找出rank[k]中每个角色是否存在于这个arena
                    rankList=[-1]+[(-1) for n in range(1,len(rank[k]))]
                    #记录每个角色在arena中的下标。第0格用rank[k][0]占位
                    j=0
                    while(j<count):#遍历arena
                        rankIndex=1
                        while(rankIndex<len(rank[k])):#遍历rank[k]
                            if(charaTable[j].find(rank[k][rankIndex])>-1):
                                rankList[rankIndex]=j
                                #已经找到角色下标。但是如果是前半部分角色没有被给数字，则需要给数字
                                if(charaValueTable[j]==0 and rankIndex<=rank[k][0]):
                                    maxValue+=1
                                    charaValueTable[j]=maxValue
                                    charaIndexTable.remove(j)
                                break
                            rankIndex+=1
                        j+=1
                    rankWorse=len(rank[k])-1#要给rank[k]中哪个下标的角色给出更差数字
                    #下面确保rankWorse所有角色比rankBetter所有角色差
                    while(rankWorse>rank[k][0]):
                        #需要使前rank[k][0]个角色比后面角色数字大
                        rankBetter=0#要给rank[k]中哪个下标的角色个给出更好数字
                        if(rankList[rankWorse]>-1):
                            while(rankBetter<=rank[k][0]):
                                #如果要给较差数字的角色目前数字不是0，而且较差角色数字比较好角色更好
                                #则交换他们的数字
                                if(rankList[rankBetter]>-1
                                   and charaValueTable[rankList[rankWorse]]>0
                                   and charaValueTable[rankList[rankBetter]]>charaValueTable[rankList[rankWorse]]):
                                    charaValueTable[rankList[rankBetter]],charaValueTable[rankList[rankWorse]]=charaValueTable[rankList[rankWorse]],charaValueTable[rankList[rankBetter]]
                                rankBetter+=1
                                #之前已经保证过较好角色的数字不是0
                        rankWorse-=1
                    #下面删除rank[k]在这个arena中出现过的角色
                    rankBetter=len(rank[k])-1
                    rankWorse=rank[k][0]+1
                    while(rankBetter>=0):
                        if(rankList[rankBetter]!=-1):
                            if(rankBetter<rankWorse):
                                rank[k][0]-=1
                            rank[k].pop(rankBetter)
                        rankBetter-=1
                k-=1

            #已经发完数字。开始生成postdata
            j=0
            while(j<len(charaTable)):
                data['contestant['+arenaToken+']['+str(j)+']']=str(j)
                data['contestant_vote['+arenaToken+']['+str(j)+']']=str(charaValueTable[j])
                j+=1
        i+=1
    
    rand=random.random()
    if(rand<0.65):
        data['gender']='male'
    elif(rand<0.95):
        data['gender']='female'
    else:
        data['gender']='abstain'
    
    rand=random.random()
    if(rand<0.62):
        data['age']='adult'
    elif(rand<0.975):
        data['age']='minor'
    else:
        data['age']='abstain'    
    
    data['captcha_input']=vcode
    
    #dataStr=str(data)
    #dataStr=dataStr.replace('\': \'','=').replace('\', \'','&').replace('[','%5B').replace(']','%5D')
    
    #with open('dataStr.cpp','w') as t:
    #    t.write(dataStr)
    
    #print(dataStr)
    #Content_length=len(dataStr)-4
    return data
    
if __name__ == '__main__':
    #html=open(r"ISML 2018 Ruby Necklace.htm",'r',encoding="utf-8").read()
    html=open(r"ISML季后赛2.htm",'r',encoding="utf-8").read()
    data=selector(html,'testVotingToken','testCaptcha')
    #print('Willem: '+data['contestant_vote[10][3]'])
    #print('Astolfo: '+data['contestant_vote[10][1]'])
    #print('Archer: '+data['contestant_vote[10][6]'])
    #print('Gilgamesh: '+data['contestant_vote[10][4]'])
    #print('Makise: '+data['contestant_vote[3][4]'])
    #print('Rinne: '+data['contestant_vote[13][1]'])
    print('Chtholly：'+data['contestant_vote[20][1]'])
