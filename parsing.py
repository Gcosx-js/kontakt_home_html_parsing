import re
import requests
import sqlite3

# QEYD RENGLER NEZERE ALINMIR VE SADECE PAGE 1 UCUN KECERLIDIR,UYGUN TELEFONLAR : IPHONE,SAMSUNG. DUZENLEMELERLE PAGE 1-DE OLAN BUTUN MEHSULLAR UCUN KECERLIDI. DATABASE NEZARET UCUN << SQLITE3 DB BROWSER >> ENDIRIN

conn = sqlite3.connect('kontakt_home_datas.db')
c = conn.cursor()
def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS Kontakt_home_datas
                 (Marka TEXT,Model TEXT,Yaddaş INTEGER,Qiymət INTEGER)''')
    
#Eger .db fayli yoxdursa asagidaki setri yorumdan cixarin 
#create_table()
    
def send_data(marka,model,yaddas,qiymet):
    c.execute("INSERT INTO Kontakt_home_datas (Marka,Model,Yaddaş,Qiymət) VALUES (?,?,?,?)", (marka,model,yaddas,qiymet))
    conn.commit()
    
def check_data(marka,model,yaddas,qiymet):
    c.execute('''SELECT * FROM Kontakt_home_datas
                      WHERE Marka = ? AND Model = ? AND Yaddaş = ? AND Qiymət = ?''',
                   (marka, model, yaddas, qiymet))
    query_data = c.fetchone()
    if query_data:
        return False #Database'de var
    else:
        return True #Yoxdur


def kontakthome_parsing(url):
    site = requests.get(url).text
    if 'apple' in url:
        r_adlar = re.compile(r'<a draggable="false" href="https://kontakt\.az/iphone[^"]*">([^<]*) </a>')
    elif 'samsung' in url:
        r_adlar = re.compile(r'<a draggable="false" href="https://kontakt\.az/samsung[^"]*">([^<]*) </a>')

    adlar = re.findall(r_adlar, site)
    r_k_qiymetler = re.compile('<span style="text-decoration:line-through;font-weight:normal">(.*?)<small class="azn_span">M</small></span>')

    k_qiymetler = re.findall(r_k_qiymetler,site)
    #print(max(k_qiymetler),adlar[k_qiymetler.index(max(k_qiymetler))])
    if len(adlar)==len(k_qiymetler):
        ip_model_keys = ['Pro','Max','Plus']
        for i in range(len(adlar)):
            marka = adlar[i].split()[0]
            if marka.lower()=='samsung': #samsunglarda model gbdan 1 indeks evvele qeder gelir
                s = 0
                for m in adlar[i].split():
                    if m=='GB': 
                        model = ' '.join(adlar[i].split()[1:(s-1)])
                    s+=1
            elif marka.lower()=='iphone': 
                model = adlar[i].split()[1]
                for key in adlar[i].split():
                    if key in ip_model_keys: #iphonelerde pro,max,plus shertin nezere almaq lazimdir
                        model=model+' ' + key
            s = 0
            for y in adlar[i].split():
                if y=='GB': #markasindan asili olmayaraq yaddasi bele aliriq
                    yaddas = adlar[i].split()[s-1]
                    break
                s+=1
            
            if check_data(marka,model,yaddas,k_qiymetler[i]): #eger yoxdursa
                send_data(marka,model,yaddas,k_qiymetler[i])  #  elave et
              
    else:
        print(False) #Datalar tutushmursa bura girecek


kontakthome_parsing('https://kontakt.az/telefonlar/mobil-telefonlar/samsung-mobil-telefonlar')
kontakthome_parsing('https://kontakt.az/telefonlar/mobil-telefonlar/apple-mobil-telefonlar')
