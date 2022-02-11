
import pandas as pd;# paquete para trabajar con dataframes
import numpy as np; #paquete para trabajar con matrices 
import selenium; #paquete para realizar web scraping dinámico
from selenium import webdriver; #paquete para abrir un navegador robotizado
import time; # paquete para trabajar con datos tipo fecha 
from webdriver_manager.chrome import ChromeDriverManager;
from selenium.webdriver.support.ui import Select;
from bs4 import BeautifulSoup #paquete para leer código HTML (web scraping estático)
class CONSULTA():
    def __init__(self):
        self.browser = webdriver.Chrome(ChromeDriverManager().install()) #Instala la versión más actual de chromium
        self.browser.get("https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx") # Abre el vínculo que se desea scrappear
        self.browser.switch_to.frame(self.browser.find_element_by_name("frame0"))
        self.pas = ''
        self.s = 'N'
        self.numero = 2022
        self.encabezados = ['Filtro','PIA_{}'.format(self.numero),'PIM_{}'.format(self.numero),'DEV_{}'.format(self.numero),'GIR_{}'.format(self.numero)]
        print("Listo! Has ingresado a la consulta")
        
    def retroceder(self):
        tabla2 = self.browser.find_element_by_xpath('//*[@id="PnlHistory"]/table') # seleccionamos la tabla registro de historial
        fila2 = tabla2.find_elements_by_tag_name('tr')
        if len(fila2)<10:
            self.browser.find_element_by_id('ctl00_CPH1_RptHistory_ctl0{}_TD0'.format(len(fila2))).click()
        elif len(fila2) >= 10:
            self.browser.find_element_by_id('ctl00_CPH1_RptHistory_ctl{}_TD0'.format(len(fila2))).click()
    
    def indices(self):
        tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
        fila = tabla.find_elements_by_tag_name('tr')
        indice = [fila[x].find_elements_by_tag_name('td')[1].text.split(':')[0] for x in range(0,len(fila))]
        return indice
    
    def AÑO(self,numero=2021):
        self.numero = numero
        año = Select(self.browser.find_element_by_name('ctl00$CPH1$DrpYear')) #Seleccionamos la lista desplegable año
        año.select_by_value(str(numero)) #Seleccionamos el año que queremos scrappear
        self.encabezados = ['Filtro','PIA_{}'.format(self.numero),'PIM_{}'.format(self.numero),'DEV_{}'.format(self.numero),'GIR_{}'.format(self.numero)]
        try:
            self.browser.switch_to.frame(self.browser.find_element_by_name("frame0"))
        except:
            pass
        print('Listo! Seleccionaste el año')
    
    def ACTIVIDADES(self,opcion='AMBOS'):
        if opcion == 'PROYECTO':
             opcion = 'Proyecto'
        elif opcion == 'ACTIVIDAD':
            opcion = 'Actividad'
        elif opcion == "AMBOS":
            opcion = 'ActProy'
        else: 
            print('No esta bien')
        
        actividades_proy = Select(self.browser.find_element_by_name('ctl00$CPH1$DrpActProy')) #Seleccionamos la lista desplegable actividades/proyectos
        actividades_proy.select_by_value(opcion) #Seleccionamos actividad o proyecto o ambos
        try:
            self.browser.switch_to.frame(self.browser.find_element_by_name("frame0"))
        except:
            pass
        print('Listo! Seleccionaste {}'.format(opcion))

    
    def GOBIERNO(self,opcion = '', s = 'N'):
        self.encabezados[0] = 'Gobierno'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnTipoGobierno').click() #Hacemos click en nivel de gob
        except:
            pass
      
        niv_gob = self.indices()
        if opcion in niv_gob:
            self.pas = self.pas.split('.')[-1] +'.GB-'+opcion
            pos = niv_gob.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en gobierno ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns=self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1] +'.GB'
            anual = pd.DataFrame(self.VALORES(),columns=self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(niv_gob)),niv_gob):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else: 
            print('Para este año no se cuenta con el nivel de gobierno {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
         
    def SECTOR(self,opcion = '',s = 'N'):
        self.encabezados[0]= 'Sector'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnSector').click() #Hacemos click en sector
        except:
            pass
        niv_sec = self.indices()
        if opcion in niv_sec:
            self.pas = self.pas.split('.')[-1] +'.SC'+opcion
            pos = niv_sec.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en gobierno ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1]+'.SC'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(niv_sec)),niv_sec):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else: 
            print('Para este año no se cuenta con el sector {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def GENERICA(self,opcion = '', s = 'N'):
        self.encabezados[0]='Generica'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnGenerica').click() #Hacemos click en generica
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de las genericas existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.GE'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la generica ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1] +'.GE'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con la generica {}'.format(opcion))
            valor = pd. DataFrame()
            return valor

    def PLIEGO(self,opcion = '',s='N'):
        self.encabezados[0]='Pliego'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnPliego').click() #Hacemos click en PLIEGO
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.PL'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en EL PLIEGO ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1] +'.PL'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con el pliego {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def FUNCION(self,opcion = '',s='N'):
        self.encabezados[0]='Funcion'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnFuncion').click() #Hacemos click en Función
        except:
            pass
        
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.FN'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            return solo_f
            
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1] +'.FN'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en funcion...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con la generica {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def FUENTE(self,opcion = '',s='N'):
        self.encabezados[0]='Fuente'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnFuenteAgregada').click() #Hacemos click en Función
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.FF'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns=self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1]+'.FF'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con la Fuente {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
        
        
    def RUBRO(self,opcion = '',s='N'):
        self.encabezados[0]='Rubro'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnRubro').click() #Hacemos click en Rubro
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.RB'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns=self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1]+'.RB'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con el rubro {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
        
        
    def DEPARTAMENTO(self,opcion = '',s='N'):
        self.encabezados[0]='Departamento'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnDepartamentoMeta').click() #Hacemos click en Función
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.DP'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1]+'.DP'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con el departamento {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
        
    def PROYECTO(self,opcion = '',sect = '01', s='N'):
        self.encabezados[0]='Proyecto'
        self.headings = ['CUI'] + self.encabezados + ['Sector']
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnProdProy').click() #Hacemos click en Función
        except:
            pass
        #ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        #if opcion in ind_lista:
         #   self.pas = self.pas.split('.')[-1]+ '.PRY'+opcion
          #  pos = ind_lista.index(opcion)
           # self.pos = pos
           # self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            #solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            #return solo_f
        if opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1]+'.PRY'
            anual = self.DESC_PROY(sect)
            anual.columns= self.headings
            return anual
        #elif opcion == 'TODO_M':
         #   for x,y in zip(range(0,len(ind_lista)),ind_lista):
          #      self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
           #     if x == 0:
            #        mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
             #   elif x > 0:
              #      mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
               #     mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            #mensual["mes"] = pd.to_datetime(mensual["mes"])
            #mensual = mensual.sort_values('mes')
            #return mensual
        else:
            print('Para este año no se cuenta con el Proyecto {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def MES(self,opcion = '',s='N'):
        self.encabezados[0]='Mes'
        self.s = s
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnMes').click() #Hacemos click en Función
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:
            self.pas = self.pas.split('.')[-1]+ '.MES'+opcion
            pos = ind_lista.index(opcion)
            self.pos = pos
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)
            return solo_f
        elif opcion == 'TODO_A':
            self.pas = self.pas.split('.')[-1]+'.MES'
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)
            return anual
        elif opcion == 'TODO_M':
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual
        else:
            print('Para este año no se cuenta con el mes {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def PASADO(self,pasado='S'):
        if pasado == 'S':
            self.s = 'S'
        elif pasado == 'N':
            self.s = 'N'
        elif pasado == 'R':
            self.pas = ''
            
    def DESC_PROY(self,sect = '01'):
        time.sleep(2)
        datos = self.PAGINA()
        prueba = datos.findAll("table", {"class": "Data"})[0].findAll('tr')
        contenido = []
        for g in range(0,len(prueba)):
            columnas = prueba[g].findAll('td')
            contenedor = [columnas[x].get_text().replace('\n','').replace(',','') if x>1 else 
                          columnas[x].get_text().replace('\n','')
                          for x in range(0,len(columnas))]
            contenedor[2:8] = [0 if x != x or x == '' else int(x)/1000000 for x in contenedor[2:8]]
            contenido.append(contenedor)
        tabla = pd.DataFrame(contenido)
        nuevo = tabla[tabla[0]!='Ficha de Proyecto\xa0']
        nuevo[['A','B']] = nuevo[1].str.split(':', 1, expand=True)
        nuevo = nuevo.drop([0],axis=1)
        oficial = nuevo[['A','B',2,3,7,8]]
        oficial = oficial.reset_index(drop=True)
        oficial['SECTOR'] = sect
        return oficial
        
            
    def PAGINA(self):
        d = self.browser.page_source
        datos = BeautifulSoup(d,'lxml')
        return datos
            
    def VALORES(self,y='A'):
                                 
        if y == 'A':
            tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
            fila = tabla.find_elements_by_tag_name('tr')
            contenido = []
            for g in range(0,len(fila)):
                contenedor = []
                if self.s == 'S':
                    contenedor.append('{}'.format(self.pas)+fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0]) #Extrae el nombre
                elif self.s == 'N':
                    contenedor.append(fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0])
                if int(self.numero) >= 2012:
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,7,8]]
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato
                elif int(self.numero) < 2012:
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,5,6]]
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato
                contenido.append(contenedor)
                
        elif y == 'F': #Extrae los valores de la fila 
            tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
            fila = tabla.find_elements_by_tag_name('tr')
            contenido = []
            g= self.pos
            contenedor = []
            if self.s == 'S':
                contenedor.append('{}'.format(self.pas)) #Extrae el nombre
            else:
                contenedor.append(fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0])
            
            if int(self.numero) >= 2012:
                dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,7,8]]
                dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                contenedor = contenedor + dato
            elif int(self.numero) < 2012:
                dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,5,6]]
                dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                contenedor = contenedor + dato
            contenido.append(contenedor)
        elif y == 'M':
            self.browser.find_element_by_name('ctl00$CPH1$BtnMes').click() #Hacemos click en mes
            tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
            fila = tabla.find_elements_by_tag_name('tr')
            contenido = []
            for g in range(0,len(fila)):
                contenedor = []
                contenedor.append(fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0] + '/{}'.format(self.numero)) #Extrae el numero del mes
                if int(self.numero) >= 2012: 
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [7,8]]
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato
                   
                elif int(self.numero) < 2012:
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"")for u in [5,6]]
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato
                contenido.append(contenedor) 
            self.retroceder()
        return contenido
    
    def CERRAR(self):
        self.browser.quit()
        print('Has cerrado sesión')
        
        