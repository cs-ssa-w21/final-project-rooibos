import requests
from bs4 import BeautifulSoup
import pandas as pd
import cpca
import jieba
from china_cities import *
import pinyin
import csv


r = requests.get("https://cnwoman-bot.github.io/evil-man/")
soup = BeautifulSoup(r.text,'html.parser')
soup.prettify()


# getting and modifying the crime list

# This function is to get all the crimes listed under a series of <div> tags,
# where the crimes are described in the text of <a> tags and linked to urls.
def get_news_within(div):
    '''
    Getting the text within a certain div tag

    Input:
        div: the certain tag

    Output:
        lst_text: (list) a list of all text under the div tag
    '''
    p = div.next_sibling.next_sibling
    lst_text = [a.text for a in p.find_all('a')]
    return lst_text

# This part deals with a small amount of cases that were
# listed in a different manner, where rather than the crimes,
# the sentences were linked with urls and the crimes were described before,
# hence requiring a different pass to retrieve the crimes.
# '判决日期' means 'sentence date' which is used to locate crimes.
text = [i.parent.text.split('\n') for i in soup.find_all('a')
        if i.text.startswith('判决日期')]

other1 = []
for t in text:
    if len(t) <= 3:
        # t is a list of strings, and normally no more than three
        # strins were used to describe a case. This is to distinguish
        # between t that includes information about more than one case.
        other1.append(t[0])
    else:
        # here we consider the lists describing more than one case.
        for s in t:
            if '判决日期' not in s:
                other1.append(s)

other1 = list(set(other1))  #avoiding duplicates

# These are some manually coded entries that are embedded
# in general narration or discussion on the webpage,
# which do not follow particular patterns.
other2 = ['新疆喀什大学文学院援疆博士王明科',
          '云南云南大学文学院副教授蔡英杰性骚扰留学生被公开处分，现任福建师范大学教授',
          '甘肃兰州大学大气科学学院副院长张文煜被曝性侵',
          '上海戏剧学院教务处处长厉震林性骚扰，已无链接',
          '央美设计学院院长宋协伟被指控性骚扰、猥亵女学生',
          '原北京中央民族大学文学院与新闻传播学院刘立刚性骚扰',
          '湖北美院偷拍女生裙底把视频发到了p站，无语，链接不放了',
          '北京电影学院阿廖莎性侵案',
          '北京电影学院侯亮平事件',
          '亳州6·15杀人案,邻居眼中的老实人,为何连杀4人',
          '四川一名大学本科男子刘某在成都开往深圳的火车上猥亵9岁女童',
          '浙大学生努某某强奸被判一年半，学校不与开除，留校察看',
          '猥亵女童的网红“豆浆王子”蒙顺宁，出狱后获得公益组织爱心帮扶',
          '西南某大学法学院22岁男生偷拍女生裙底',
          '陕西安康石泉30岁的男子索爱一女子不成跳江自杀，女子被判决赔偿各项损失七万元']

# '本小节合计' means 'the sum of this section', which can locate the <div> tags
# with crimes listed under them.
div = [d for d in soup.find_all('div',class_ = "language-plaintext highlighter-rouge")
       if '本小节合计' in d.text]
crime = []
for d in div:
    crime += get_news_within(d)
crime += other1
crime += other2

# removing crimes where the <a> text is the name of the webpage ('知乎问题')
# where the crime was reported; in these cases the crimes themselves
# were part of the narration and hence manually added
crime = [c for c in crime if c != '知乎问题']

# removing crimes happened in Taiwan, Hong Kong, Macau
# as other datasets do not include them
crime = [l for l in crime if '台湾' not in l and '香港' not in l and '澳门' not in l]

# manually dropping crimes happened overseas
# and cases that are not about particular incidents
manual_drop = ['澳洲华人男子罗浩灵疑残忍杀妻，藏尸公寓冰柜！带俩娃逃回国，刚刚被捕',
                '澳洲华人男子胡伟杀妻后自杀，8岁儿子在旁目睹全过程',
                '美国纽约州威彻斯特郡46岁的华裔男子刘传凯杀死妻子和俩孩子后自杀身亡',
                '新加坡一中国籍男子Cui Huan谋杀妻子，罪成将面对死刑或终身监禁兼鞭刑',
                '泰国华裔男子喂刚出生7天的女儿洁厕剂，杀害并埋尸坟地',
                '留日女学生江歌被闺蜜刘鑫前男友陈世峰捅刀杀死',
                '澳大利亚国立大学中国留学生Junqi Huang浴室偷拍被捕，遭校方开除。曾任超级脑学会的前任主席',
                '美国伊利诺伊大学厄巴纳-香槟分校华人教授徐钢性侵女学生',
                '我是包丽的朋友，真相远比你知道的更可怕',
                '日本东京街头一中国籍男子强摸女性被捕',
                '女友爆料罗志祥多次出轨，参与多人群p',
                '女医护人员剃光头“是否自愿”遭质疑，网友：唯一男医生是平头',
                '只要我不报道女性，不宣传女性，所有的功劳就还是男性的',
                '“洋媳妇”与“洋女婿”双重标准纪实',
                '各项扶贫政策落实后，某贫困户要求给他分配个女人',
                '“致良知四合院”会场宣传女性应该完全服从男性',
                '女德班成果：“中国女孩只属于中国男孩”',
                '泰国乌汶府Pha Taem国家公园一江苏男子俞某杀妻谋财',
                '泰国春武里府的海滩，中国台湾男子卢子扬杀妻抛尸',
                '泰国一家酒店的泳池中天津男子张轶凡杀妻骗保',
                '韩国一中国籍游客男子陈某在天主教堂杀害一名女路人']

crime = [c for c in crime if c not in manual_drop]

# dropping cases happened on cross-city transportations as the city would be difficult to identify
# '开往' means 'drive to','火车' means train and '火车站' means train station.
# We still keep the cases happened in stations as those cities are identifiable.
transport = [c for c in crime if '开往' in c or ('火车' in c and '火车站' not in c)]
crime = [c for c in crime if c not in transport]


# Building the city dictionary from an existent json file

#The keys are cities and the values are corresponding made up of
#three components:
#the city's subordinate units in both abbreviated version and full version,
#the city in both abbreviated version and full version,
#its province (if any) in both abbreviated version and full version.

url = ("https://raw.githubusercontent.com/adyliu"
       "/china_area/master/area_code_2020.json")
df = pd.read_json(url)
dct_city={}

# Location units have five different levels in China, from province
# to villages; we only consider cities at level 1 and 2 as they align
# with the general perception of cities better.
for row in df.iterrows():
    prov = row[1]['name']
    for dct in row[1]['children']:
        if dct['name'] == '市辖区' and dct['level'] == 2:
            # if cities are level 1, they don't belong to
            # any province so their 'name' in the 'children'
            # would be '市辖区' ('city districts'); here the
            # province would be the city
            key = prov
        elif dct['level'] == 2:
            # considering only level 2 cities now
            key = dct['name']
        if key.endswith('行政区划') == False and len(key) > 1:
            # '行政区划' also means districts rather than cities
            # so we drop these terms.
            # Because official names are used here,
            # each city is named with the word 'city'('市'),
            # hence making it at least 2 characters long

            # finding the subordinate units, e.g. counties
            rel_city = [d['name'] for d in dct['children']]

            # adding prov as a related unit
            rel_city.append(prov)

            # adding usual abbreviations of city names as they
            # are used often in news
            sim_city = [c[:-1] for c in rel_city if len(c) >= 3]
            rel_city += sim_city

            # adding the city's abbreviation
            rel_city.append(key[:-1])

            dct_city[key] = set(rel_city)



# Building a university dictionary as some cases were located in universities

# The keys are cities and the values are universities in that city

url = ("https://raw.githubusercontent.com/WenryXu/"
        "ChinaUniversity/master/ChinaUniversityList.json")
df_uni = pd.read_json(url)
dct_uni = {}

for l in df_uni.schools:
    for d in l:
        c = d['city']
        n = d['name']
        if c in dct_uni.keys():
            dct_uni[c] += [n]
        else:
            dct_uni[c] = [n]

# remove universities in Taiwan because
# we do not consider cases in Taiwan
# and there are Chinese universities
# sharing the sames
del dct_uni['台湾省']
del dct_uni['香港特别行政区']
del dct_uni['澳门特别行政区']

# matching crimes

left_crime = crime[:]
lst_ma = []
dct_m = {}

def match_uni(string,u):
    '''
    Matching a crime case string to a city

    Input:
        string: (string) the crime string
        u: (string) the keyword ('大学university'/'学院college')
            to help locate university names
    '''
    city = None
    ind = [i for i in range(len(string)) if string[i] == u[0]][0]
    key = string[0:ind + 2]
    if key in lst_val:
        # if university name is the first term in the string
        # This is a valid assumption as news are usually reported
        # with location upfront.
        city = [k for k in dct_uni.keys() if key in dct_uni[k]][0]
        if city in dct_m.keys():
            dct_m[city] += 1
        else:
            dct_m[city] = 1
        if string in left_crime:
            left_crime.remove(string)
            lst_ma.append((string,city))

    else:
        # if university is not the first term
        set_w = jieba.cut(string)
        # the jieba library can cut strings into terms that
        # make sense and usually full names of universities
        # will be one term.
        set_uni = {w for w in set_w if u in w}
        if len(set_uni) > 0:
            # choosing the longest term because even if other
            # terms have the keyword within, the full name of
            # university would be the longest one
            uni = [w for w in set_uni if len(w) ==
                    max({len(t) for t in set_uni})][0]
            if uni in lst_val:
                city = [k for k in dct_uni.keys() if uni in dct_uni[k]][0]
                if city in dct_m.keys():
                    dct_m[city] += 1
                else:
                    dct_m[city] = 1
                left_crime.remove(string)
                lst_ma.append((string,city))


lst_val = []
# creating a list of all universities to see if a university is included
# in the dictionary values
for v in dct_uni.values():
    lst_val += v
for l in crime:
    if '大学' in l:
        # if the term 'university' is included,
        # the keyword would be 'university'
        match_uni(l,'大学')
    elif '学院' in l:
        # if the term 'college' is included,
        # the keyword would be 'college'
        match_uni(l,'学院')
    if ('北大' in l or '清华' in l) and l in left_crime:
        # '北大' is an abbreviation for PKU and '清华' for THU in Beijing.
        # The universities are too well-known that most of the times
        # people do not call them by their full names but these abbreviations.
        if '北京市' not in dct_m.keys():
            dct_m['北京市'] = 1
        else:
            dct_m['北京市'] += 1
        left_crime.remove(l)
        lst_ma.append((l,'北京市'))

# manually adding cases where university names are abbreviated,
# which cannot be matched as these abbreviations are not generated on
# a unanimous standard, or where some professors' names are given
# but the universities need to be inferred
uni_c = '央美国画系教授丘挺多次与多位女学生发生关系，其妻欲跳楼轻生'
left_crime.remove(uni_c)
dct_m['北京市'] += 1
lst_ma.append((uni_c,'北京市'))

uni_c = '央美国画系教授姚舜熙被学生联合实名举报x骚扰、以权谋私、诽谤等'
left_crime.remove(uni_c)
dct_m['北京市'] += 1
lst_ma.append((uni_c,'北京市'))

uni_c = '北航教授陈小武被举报性骚扰 疑似曾致手下学生怀孕'
left_crime.remove(uni_c)
dct_m['北京市'] += 1
lst_ma.append((uni_c,'北京市'))

uni_c = '女学生遭HYD博导凌昌全教授十五年骚扰、打击报复、逼迫就范'
left_crime.remove(uni_c)
dct_m['上海市'] += 1
lst_ma.append((uni_c,'上海市'))

uni_c = '哈工大男生在网上用污言秽语辱骂师大女生'
left_crime.remove(uni_c)
dct_m['哈尔滨市'] = 1
lst_ma.append((uni_c,'哈尔滨市'))

uni_c = '厦大海洋与海岸带发展研究院在读硕士彭炜敏\
婚内出轨，并假冒母亲身份欺骗女生'
left_crime.remove(uni_c)
dct_m['厦门市'] += 1
lst_ma.append((uni_c,'厦门市'))

uni_c = '浙大央美性搔扰惯犯崔青洲'
left_crime.remove(uni_c)
dct_m['杭州市'] = 1
lst_ma.append((uni_c,'杭州市'))

uni_c = '央美设计学院院长宋协伟被指控性骚扰、猥亵女学生'
left_crime.remove(uni_c)
dct_m['北京市'] += 1
lst_ma.append((uni_c,'北京市'))

uni_c = '浙大学生努某某强奸被判一年半，学校不与开除，留校察看'
left_crime.remove(uni_c)
dct_m['杭州市'] += 1
lst_ma.append((uni_c,'杭州市'))

uni_c = '北工大外国语学院男生吴江掐死女友续：凶手被判死缓'
left_crime.remove(uni_c)
dct_m['北京市'] += 1
lst_ma.append((uni_c,'北京市'))


# matching other cases by searching for locations
def cpca_match(s):
    '''
    Retriving the city information from a crime string

    Input:
        s: (string) the crime string to be analysed

    Output:
        city: (string) the city retrieved
    '''
    df = cpca.transform([s])
    row = df.iloc[0,]
    city = row['市']
    prov = row['省']
    if prov != None and prov.endswith('市'):
        # this deals with the special cities like Beijing
        # that belongs to no province; so the province name
        # ends with '市' meaning 'city'
        city = prov
        return city
    else:
        if city != None:
            if city.endswith('行政区划') == False:
                # '行政区划' means 'districts' so if a term
                # ends with it, it will not be a city as we define
                return city
        else:
            if '首都' in s:
                # '首都' means capital but does not exist in the dictionary keys
                city = '北京市'
            else:
                lst_w = list(jieba.cut(s))
                del_ind = len(lst_w[0])
                if len(s) > del_ind:
                    city = cpca_match(s[del_ind:])
                    # this recursion is used here because normally each crime
                    # is described with its location upfront, but sometimes
                    # the locations can be wrong, leading to the city
                    # equalling None,or the locations were stated
                    # after some description,so we divide the string
                    # into keywords by the jieba library and remove the
                    # keywords once at a time until we can locate the city
                    # or retrieve no information
            return city


def county_match(s):
    '''
    Retriving the city information from a crime string
    based on county information (if any)

    Input:
        s: (string) the crime string to be analysed

    Output:
        city: (string) the city retrieved
    '''
    row = cpca.transform([s]).iloc[0,]
    prov = row['省']
    if prov != None and row['市'] == None and row['区'] == None:
        # This is the case where cities cannot be identified
        # but provinces can, so we focus on the remaining string
        # without the province term to avoid provinces interfering
        s = row['地址']
    else:
        # In some cases locations are wrongly matched,
        # leading to the '市'/city column or '区'/district
        # column not being None, so we disregard all these
        # circumstances and analyse the original string.
        prov = None
    set_w = set(jieba.cut(s))

    if prov != None:
        # narrowing the possible cities based on provinces
        potential = [c for c in dct_city.keys() if prov in dct_city[c]]
    else:
        potential = dct_city.keys()

    # Because most county names are unique, especially
    # after pinning down provinces, the cities those values share the
    # most common terms with the string term set should be the most
    # likely cities.
    max_sim = 0
    cities = []
    city = None
    for k in potential:
        sim = len(dct_city[k] & set_w)
        if sim > max_sim:
            max_sim = sim
            cities = [k]
        elif sim != 0 and sim == max_sim:
            cities.append(k)
    if len(set(cities)) == 1:
        # if there is only one likely city, it will be the city
        city = cities[0]
    else:
        # When more than 1 cities or no cities are included,
        # sometimes it is because the abbreviation of the county names
        # are differently constructed to most other counties. Because
        # the dictionary values are essentially sets of strings,
        # abbreviation may not be found when searching through the sets,
        # but can be found when searching through strings in the sets,
        # which is why this step is conducted separately to the last.
        lst_city = []
        key = list(jieba.cut(s))[0]
        county_sim = 0
        for c in potential:
            v = dct_city[c]
            ct_sim = len([ct for ct in v if key in ct])
            if ct_sim > county_sim:
                county_sim = ct_sim
                lst_city = [c]
            elif ct_sim != 0 and ct_sim == county_sim:
                lst_city.append(c)
        if len(lst_city) == 1:
            city = lst_city[0]
    return city

leftover = left_crime[:]
for c in leftover:
    city = cpca_match(c)
    if city == None:
        city = county_match(c)
    if city != None:
        if city in dct_m.keys():
            dct_m[city] += 1
        else:
            dct_m[city] = 1
        left_crime.remove(c)
        lst_ma.append((c,city))


# manually editing some wrongly matched crimes mainly
# because some criminals' names are also city names,
# or there are multiple locations within the sentence
# and the first is not the crime location, or cannot be matched
# with the above codes

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '辽宁凌源籍男子占某在江苏南通市市区钟楼广场地下通道处偷袭猥亵过路女子'][0]
lst_ma[ind] = ('辽宁凌源籍男子占某在江苏南通市市区钟楼广场地下通道处\
偷袭猥亵过路女子','南通市')
dct_m['南通市'] += 1
dct_m['朝阳市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '甘肃青海大通县多林镇吴仕庄村男子蔡某与妻子不和，杀妻子全家后自杀'][0]
lst_ma[ind] = ('甘肃青海大通县多林镇吴仕庄村男子蔡某与妻子\
不和，杀妻子全家后自杀','西宁市')
dct_m['西宁市'] = 1
dct_m['重庆市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '辽宁建昌县农贸市场宏大东北大药房一男子王某军持匕首当场捅死前妻'][0]
lst_ma[ind] = ('辽宁建昌县农贸市场宏大东北大药房一男子王某军\
持匕首当场捅死前妻','葫芦岛市')
dct_m['葫芦岛市'] += 1
dct_m['北京市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '原北大教师沈阳被指“性侵女生致其自杀”'][0]
lst_ma[ind] = ('原北大教师沈阳被指“性侵女生致其自杀','南京市')
dct_m['南京市'] += 1
dct_m['北京市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '贵州紫云县一父亲强奸20岁亲生女儿长达6年 一审被判12年'][0]
lst_ma[ind] = ('贵州紫云县一父亲强奸20岁亲生女儿长达6年 一审被判12年','安顺市')
dct_m['安顺市'] = 1
dct_m['临沧市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '山东陵县宋家镇东屯村农民郭永庆掐死女友'][0]
lst_ma[ind] = ('山东陵县宋家镇东屯村农民郭永庆掐死女友','德州市')
dct_m['德州市'] += 1
dct_m['重庆市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '云南巍山县大仓镇男子段金泉杀害6名年轻女性'][0]
lst_ma[ind] = ('云南巍山县大仓镇男子段金泉杀害6名\
年轻女性','大理白族自治州')
dct_m['大理白族自治州'] += 1
dct_m['重庆市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '福建厦门一女患者在复旦大学附属医院厦门分院更衣室换衣服被男子观看\
全程，医院：不能说是偷窥！'][0]
lst_ma[ind] = ('福建厦门一女患者在复旦大学附属医院厦门分院更衣室换衣服被\
男子观看全程，医院：不能说是偷窥！','厦门市')
dct_m['厦门市'] += 1
dct_m['上海市'] -= 1

ind = [i for i in range(len(lst_ma)) if lst_ma[i][0] ==
        '福建龙岩武平男子钟某鸣将女子诱骗至其厦门\
暂住处，用其手机申请网络贷款并将其杀害'][0]
lst_ma[ind] = ('福建龙岩武平男子钟某鸣将女子诱骗至其厦门\
暂住处，用其手机申请网络贷款并将其杀害','厦门市')
dct_m['厦门市'] += 1
dct_m['龙岩市'] -= 1

l = '江西玉山一湖南籍男子张某猥亵女学生和女老师'
left_crime.remove(l)
dct_m['上饶市'] += 1
lst_ma.append((l,'上饶市'))

l = '西南某大学法学院22岁男生偷拍女生裙底'
left_crime.append(l)
dct_m['黔西南布依族苗族自治州'] -= 1
lst_ma.remove((l,'黔西南布依族苗族自治州'))


# matching to English names and writing into csv

# constructing a dictionary matching city Chinese names to English ones
dct_lang = {}

for c in cities.get_cities():
    if c.name_cn in dct_m.keys():
        dct_lang[c.name_cn] = (c.name_en,c.province)
        # Province was added because some cities of different provinces
        # share the same English names.

# Because different collection of cities, some cities are missing
# in the library, so we add them using normal translation norms.
lst_special = [c for c in dct_m.keys() if c not in dct_lang.keys()]

special = lst_special[:]
for ct in special:
    key = list(jieba.cut(ct,cut_all=True))[0]
    # This is to disentangle some measure units like 'city'
    # or 'self-governing state' which can be coded differently
    # in different library/datasets; but as the measure units are
    # always behind the names, selecting the first element
    # can usually derive the name.
    eng = [(c.name_en,c.province) for c in
            cities.get_cities() if key in c.name_cn]
    if len(eng) == 1:
        dct_lang[ct] = eng[0]
        lst_special.remove(ct)
    else:
        # If the name is not in the dataset, we translate ourselves.
        eng_name = pinyin.get(key, format="strip",
                     delimiter="").capitalize()
        # getting the pinyin of the name
        prov = [c for c in dct_city[ct] if c.endswith('省')][0]
        # finding its province
        prov_eng = pinyin.get(prov[:-1], format="strip",
                    delimiter="").capitalize()
        # getting the pinyin for the province
        dct_lang[ct] = (eng_name,prov_eng)
        lst_special.remove(ct)


# removing cities with 0 crimes
l_rmkey = []
for k in dct_m.keys():
    if dct_m[k] == 0:
        l_rmkey.append(k)

for k in l_rmkey:
    del dct_m[k]


# writing into CSV files
lst_result = []
for k,v in dct_m.items():
    tup = (dct_m[k],k,dct_lang[k])
    lst_result.append(tup)
lst_result.sort()

with open("data.csv","w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['number of cases','location_CN','location_ENG'])
    for l in lst_result:
        writer.writerow(l)

with open("matches.csv","w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['case','location'])
    for l in lst_ma:
        writer.writerow(l)