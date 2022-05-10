import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime

geolocator = Nominatim(user_agent="leilao")

headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

template="""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>Placemark.kml</name>
	<open>1</open>
	<LookAt>
		<longitude>%longcenter%</longitude>
		<latitude>%latcenter%</latitude>
		<altitude>0</altitude>
		<heading>0</heading>
		<tilt>45</tilt>
		<range>5000</range>
		<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
	</LookAt>
	<Style id="sh_red-circle">
		<IconStyle>
			<scale>1.77273</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
			</Icon>
			<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
		</IconStyle>
		<BalloonStyle>
		</BalloonStyle>
		<ListStyle>
			<ItemIcon>
				<href>http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png</href>
			</ItemIcon>
		</ListStyle>
	</Style>
	<StyleMap id="msn_red-circle">
		<Pair>
			<key>normal</key>
			<styleUrl>#sn_red-circle</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#sh_red-circle</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="sn_red-circle">
		<IconStyle>
			<scale>1.5</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
			</Icon>
			<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
		</IconStyle>
		<BalloonStyle>
		</BalloonStyle>
		<ListStyle>
			<ItemIcon>
				<href>http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png</href>
			</ItemIcon>
		</ListStyle>
	</Style>
  %pontos%
</Document>
</kml>
"""

placemark="""
<Placemark>
		<name>%titulo%</name>
		<open>%ordem%</open>
    <description>%descricao%</description>
		<LookAt>
			<longitude>%long%</longitude>
			<latitude>%lat%</latitude>
			<altitude>0</altitude>
			<heading>-0.0001574028287822766</heading>
			<tilt>45.00741846457245</tilt>
			<range>2168.20404455787</range>
			<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
		</LookAt>
		<styleUrl>#msn_red-circle</styleUrl>
		<Point>
			<gx:drawOrder>1</gx:drawOrder>
			<coordinates>%long%,%lat%,0</coordinates>
		</Point>
	</Placemark>
"""

class Leilao:
  def __init__(self,cidade,estado,tipo=0):
    if tipo == 0:
      url = 'https://www.leilaoimovel.com.br/leilao-de-imovel/'+cidade+"/"
    else:
      url = "https://www.leilaoimovel.com.br/encontre-seu-imovel/?keyword=&states=&location="+cidade+"&type="+tipo
    
    columns = ["CIDADE", "IMOVEL","LEILAO","ENDERECO", "DETALHES","LINK1","LINK2","LAT","LONG","TIMESTAMP"]
    self.columns = columns
    df = pd.DataFrame(columns = self.columns)
    self.df = df
    self.estado = estado
    self.cidade = cidade
    self.lat = 0
    self.lon = 0
    self.cid = self.cidade.replace("-"," ").title()
    self.tipo = tipo
    self.url = url
    self.npages()
    self.imoveis()
    self.atualizarbanco()
    self.tocsv()
    self.tokml()   
    
  def imoveis(self):
    for page in range(1,self.pages+1,1):
      if page==1:
        nurl = self.url
      else:
        if self.tipo==0:
          nurl = self.url + "page/" + str(page) + "/"
        else:
          nurl = "https://www.leilaoimovel.com.br/encontre-seu-imovel/page/"+str(page)+"/?keyword=&states=&location="+self.nome+"&type="+self.tipo
      soup = bs(requests.get(str(nurl),timeout=10, headers=headers).content, "html.parser")
      #print (nurl)
      for card in soup.find_all("div", {"class": "card"}):
        s_details = ""
        title = card.find("h2", {"class": "item-title"}).text.strip()
        tipo = title.split(" ")[0]
        leilao = title.split(" ")[-1]
        adress = card.find("address", {"class": "item-address"}).text.strip().replace(","," ").replace("nº"," ")
        details = card.find("ul", {"class": "item-price-wrap"}).find_all("li")
        a = card.find("h2", {"class": "item-title"}).find("a")
        href = a['href']
        #link = self.linkleilao(href)
        link = "CARREGAR"
        for detail in details:
          s_details += str(detail.text) +" "
        #lat, lon = self.latlon(adress)
        lat, lon = 0,0
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        row = pd.DataFrame([[self.cidade, tipo,leilao, adress,s_details,href,link,lat,lon,timestamp]], columns = self.columns)
        self.df = self.df.append(row, ignore_index=True)

  def npages(self):
    soup = bs(requests.get(self.url,timeout=10,headers=headers).content, "html.parser")
    last = 1
    try:
      page = soup.find("ul", {"class":"pagination"}).find_all("a", {"class": "page-link"})
      for link in page:
        try:
          nb = int(link.text)
          if nb > last:
            last = nb
        except:
          continue
    except:
      a=1
    self.pages=last

  def print(self):
    print("URL=", self.url)
    print("QTY=", self.df.shape[0])
    print("PAGES=", self.pages)
    for index, row in self.df.iterrows():
      print (index, row["IMOVEL"],row["LINK2"],row["DETALHES"],row["LEILAO"])


  def latlon(self, adress):
    location = geolocator.geocode(adress, timeout=10000)
    if location==None and self.lat==0:
      location = geolocator.geocode(self.cid+" "+self.estado+" brasil", timeout=10000)
      self.lat, self.lon  = location.latitude, location.longitude
      Loc = self.lat, self.lon
    elif location ==None and self.lat!=0:
      Loc = self.lat, self.lon  
    else:
      Loc = location.latitude,location.longitude
    return Loc

  def tocsv(self):
    df = self.df
    df.to_csv(self.cidade+".csv",index=False)

  def tokml(self):
     df = self.df
     count = 1
     pontos = ""
     for index, row in df.iterrows():
       detalhes =""
       lat, lon, = str(row["LAT"]), str(row["LONG"])
       titulo = "#"+str(count)+" "+str(row["IMOVEL"])
       endereco = row["ENDERECO"]
       detalhes = row["DETALHES"]
       href = row["LINK1"]
       descricao = endereco+detalhes+href
       count+=1
       ponto = placemark.replace("%long%", lon).replace("%lat%", lat).replace("%ordem%",str(count)).replace("%titulo%",titulo).replace("%descricao%",descricao)
       pontos = pontos.strip() + ponto.strip()

     main = template.replace("%latcenter%",str(self.lat)).replace("%longcenter%",str(self.lon)).replace("%pontos%",pontos).strip()
     with open(self.cidade+".kml", 'w') as f:
       f.write(main)
     with open(self.cidade, 'w') as f:
       f.write(main)

  def linkleilao(self, link):
    soup = bs(requests.get(link,timeout=10,headers=headers).content, "html.parser")
    html = soup.find("input" ,{"id":"url_leiloeiro"})
    if html ==None:
      link = "IMOVEL CAIXA"
    else:
      link = html['value'].replace("?utm_source=Leilao%2520Imovel&utm_medium=Link%2520Leilao%2520Imovel","").replace("utm_source=Leilao%2520Imovel&utm_medium=Link%2520Leilao%2520Imovel","")
    return str(link)

  def atualizarbanco(self):
    new_data = pd.DataFrame(columns = self.columns)
    df = self.df
    url = "https://afonso911.pythonanywhere.com/getdata"
    content = requests.get(url,timeout=10,headers=headers).content
    data_id = pd.read_json(content, orient ='index')
    count=0
    for id in df["LEILAO"]:
      try:
        flag = data_id.eq(int(id)).sum().values[0]
      except:
        flag = 0
      if flag == 0:
        href = df.loc[count,"LINK1"]
        link = self.linkleilao(href)
        adress = df.loc[count,"ENDERECO"]
        lat, lon = self.latlon(adress)
        df.loc[count,"LINK2"] = link
        df.loc[count,"LAT"] = lat
        df.loc[count,"LONG"] = lon 
        new_data = new_data.append(df.loc[count],ignore_index=True)    
      count+=1
    if new_data.empty == False:
      url = "https://afonso911.pythonanywhere.com/postdata"
      post = requests.post(url,new_data.to_json(orient = 'index'))
      #print (post.status_code)  
    self.new=new_data

  def results(self):
   print ("FOUND:::",self.df.shape[0],"NEW:::",self.new.shape[0])


lista = Leilao("aracatuba","sao paulo").results()
