from bs4 import BeautifulSoup as bs
import requests as req
import re

def DebugOutHtml(soup):
	with open("outSoup.html", "w") as file:
		file.write(str(soup))

def DebugOutRoute(route_list):
	with open("route.txt", "w") as file:
		for route in route_list:
			file.write(str(route)+"\n")

def ParseStations(soup):
	stations=[];hrefs=[]
	tbody=soup.find('td',class_='textarea')
	tbody=tbody.findAll('a')
	for line in tbody:
		stations.append(line.text)
		hrf=line['href'];hrf=re.findall(r'\d+', hrf)
		hrefs.append(str(hrf[0]))
	return stations,hrefs

def ParseTable(soup):
	data=[]
	tbody=soup.find('fieldset')	
	rows = tbody.find_all('tr')
	for row in rows:
		cols = row.find_all('td')[:3]
		for col in cols:
			data.append(col.text.strip())
	return data

def getSearchList(station):
	stations=[];hrefs=[]
	load={'stext':station,'sub':'Искать','page':'search','city':'arhangelsk'}
	request=req.get('http://appp29.ru/mobile/op.php',params=load)
	soup = bs(request.text, 'html.parser')
	stations,hrefs=ParseStations(soup)
	return stations,hrefs

def getTable(href):
	table=[] 
	load={'city':'arhangelsk','page':'forecasts','stid':href,'rt':'А','ref':'search','stext':''}
	request=req.get('http://appp29.ru/mobile/op.php',params=load)
	soup = bs(request.text,'html.parser')	
	table=ParseTable(soup)
	return table

def getRouteList(case):
	data={}
	routes=[];hrefs=[]
	load={'city':'arhangelsk','page':'routes','rt':'А'}
	request=req.get('http://appp29.ru/mobile/op.php',params=load)
	soup = bs(request.text, 'html.parser')
	routes,hrefs=ParseStations(soup)
	data=dict(zip(routes,hrefs))
	routes,hrefs=searchDic(data,case)
	return routes,hrefs

def getRouteTables(case):
	load={'city':'arhangelsk','page':'stations','rid':case,'rt':'А'}
	request=req.get('http://appp29.ru/mobile/op.php',params=load)
	soup = bs(request.text, 'html.parser')
	stations,hrefs=ParseStations(soup)
	return stations,hrefs

def splitList(lst,chunk):
  return [lst[i:i+chunk] for i in range(0,len(lst),chunk)]


def searchDic(dic,case):
  data=[];hrefs=[]
  for key,value in dic.items():
    yolo=re.findall(r'\d+',key)
    if yolo[0]== case:
      data.append(key);hrefs.append(value)
  return data,hrefs
