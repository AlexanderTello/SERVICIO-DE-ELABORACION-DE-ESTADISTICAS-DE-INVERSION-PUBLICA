#--------------------------------------------------------------------------------------------------------------------------
#                                   Codificación del Scrapper Consulta Amigable
#--------------------------------------------------------------------------------------------------------------------------

import pandas as pd;# paquete para trabajar con dataframes
import numpy as np; #paquete para trabajar con matrices 
import selenium; #paquete para realizar web scraping dinámico
from selenium import webdriver; #paquete para abrir un navegador robotizado
import time; # paquete para trabajar con datos tipo fecha 
from webdriver_manager.chrome import ChromeDriverManager;#paquete para la descarga del navegador Chrome de prueba
from selenium.webdriver.support.ui import Select; #Funcionalidades de selenium 
from selenium.webdriver.common.by import By #paquete para realziar una accion de acuerdo a característica 
from bs4 import BeautifulSoup #paquete para leer código HTML (web scraping estático)


class CONSULTA():# Inicia el scrapper 
    def __init__(self): #Definición de inicio de clase 
        self.browser = webdriver.Chrome(ChromeDriverManager().install()) #Instala la versión más actual de chromium
        self.browser.get("https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx") # Abre el vínculo que se desea scrappear
        self.browser.switch_to.frame(self.browser.find_element_by_name("frame0"))#Cambia al frame en el que estan los botones
        self.pas = ''#Crea una variable vacia (para hacer un identificador en caso se requiera)
        self.s = 'N'#Crea una variable string relacionado a la creacion de tablas en las proximas funciones
        self.numero = 2022#esta variable cambiará cuando se seleecione año, mientra tanto será 2022
        #Se definen encabezados que cambiarán dependiendo del año
        self.encabezados = ['Filtro','PIA_{}'.format(self.numero),'PIM_{}'.format(self.numero),'DEV_{}'.format(self.numero),'GIR_{}'.format(self.numero)]
        print("Listo! Has ingresado a la consulta")
        
    def retroceder(self):#Función para regresar a la tabla anterior 
        tabla2 = self.browser.find_element_by_xpath('//*[@id="PnlHistory"]/table') # seleccionamos la tabla registro de historial
        fila2 = tabla2.find_elements_by_tag_name('tr')#buscamos el numero de filas
        if len(fila2)<10:# si el largo de las filas es menor a 10 hacer click en la última fila (cambia lo que está en {}) 
            self.browser.find_element_by_id('ctl00_CPH1_RptHistory_ctl0{}_TD0'.format(len(fila2))).click()
        elif len(fila2) >= 10:# si el largo de las filas es mayor igual a 10 hacer click en la última fila (cambia lo que está en {}) 
            self.browser.find_element_by_id('ctl00_CPH1_RptHistory_ctl{}_TD0'.format(len(fila2))).click()
    
    def indices(self):#Función para extraer los identificadores de la tabla
        tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
        fila = tabla.find_elements_by_tag_name('tr')#extrae las filas de la tabla 
         #extrae el conjunto de identificadores de cada tabla 
        indice = [fila[x].find_elements_by_tag_name('td')[1].text.split(':')[0] for x in range(0,len(fila))]
        return indice #devuelve los identificadores como una lista 
    
    def AÑO(self,numero=2021):#función para cambiar de año la consulta amigable
        self.numero = numero #la variable self.numero cambia según el año seleccionado 
        año = Select(self.browser.find_element_by_name('ctl00$CPH1$DrpYear')) #Seleccionamos la lista desplegable año
        año.select_by_value(str(numero)) #Seleccionamos el año que queremos scrappear
        #los encabezados cambian según el año seleccionado 
        self.encabezados = ['Filtro','PIA_{}'.format(self.numero),'PIM_{}'.format(self.numero),'DEV_{}'.format(self.numero),'GIR_{}'.format(self.numero)]
        try:
            #en caso sea necesario, cambiar al frame donde estan los botones
            self.browser.switch_to.frame(self.browser.find_element_by_name("frame0"))
        except:
            pass # en caso no se requiera el paso anterior, no hacer nada
        print('Listo! Seleccionaste el año')
    
    def ACTIVIDADES(self,opcion='AMBOS'):#función para filtrar por solo proyectos o actividades 
        #Dependiendo de la opcion se hará click en la lista desplegable
        if opcion == 'PROYECTO':
             opcion = 'Proyecto'
        elif opcion == 'ACTIVIDAD':
            opcion = 'Actividad'
        elif opcion == "AMBOS":
            opcion = 'ActProy'
        else: 
            print('No esta bien')#se refiere a que no esta bien escrito 
        #Seleccionamos la lista desplegable actividades/proyectos
        actividades_proy = Select(self.browser.find_element_by_name('ctl00$CPH1$DrpActProy')) 
        actividades_proy.select_by_value(opcion) #Seleccionamos actividad o proyecto o ambos
        try:
            self.browser.switch_to.frame(self.browser.find_element_by_name("frame0"))
        except:
            pass
        print('Listo! Seleccionaste {}'.format(opcion))

    
    def GOBIERNO(self,opcion = '', s = 'N'):#funcion para filtrar por nivel de gobierno 
        self.encabezados[0] = 'Gobierno' #colocal nombre de selección en encabezados
        self.s = s #Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnTipoGobierno').click() #Hacemos click en nivel de gob
        except:
            pass
        niv_gob = self.indices()#extrae los indices de la tabla
        if opcion in niv_gob:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1] +'.GB-'+opcion #Agrega nivel de gob al historial
            pos = niv_gob.index(opcion) #Busca la posicion del boton en la lista indice
            self.pos = pos #Guarda la posicion 
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en gobierno ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns=self.encabezados) #Crea la tabla con los encabezados y datos 
            return solo_f #Devuelve la tabla solo de la fila 
        elif opcion == 'TODO_A': #Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1] +'.GB' #Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns=self.encabezados) #Crea la tabla 
            return anual#Devuelve la tabla
        elif opcion == 'TODO_M': #Caso en el que se quieren extraer los datos mensuales de toda la tabla observable 
            for x,y in zip(range(0,len(niv_gob)),niv_gob): #Va iterar para cada fila 
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en fila...
                if x == 0: #Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0: #Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"]) #La columna mes se pasa a fecha 
            mensual = mensual.sort_values('mes') #Se ordena la tabla fecha 
            return mensual#Devuelve la tabla mensual 
        else: #En caso no se especifique opcion deveulve tabla vacia 
            print('Para este año no se cuenta con el nivel de gobierno {}'.format(opcion))
            valor = pd. DataFrame() 
            return valor
         
    def SECTOR(self,opcion = '',s = 'N'):#funcion para filtrar por nivel de gobierno 
        self.encabezados[0]= 'Sector' #colocal nombre de selección en encabezados
        self.s = s #Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnSector').click() #Hacemos click en sector
        except:
            pass
        niv_sec = self.indices()#extrae los indices de la tabla
        if opcion in niv_sec:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1] +'.SC'+opcion #Agrega seleccion al historial
            pos = niv_sec.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion 
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en seleccion
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados) #Crea la tabla con los encabezados y datos 
            return solo_f#Devuelve la tabla solo de la fila 
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1]+'.SC'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#Devuelve la tabla
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable 
            for x,y in zip(range(0,len(niv_sec)),niv_sec):#Va iterar para cada fila 
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en gobierno ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual 
        else: #En caso no se especifique opcion deveulve tabla vacia 
            print('Para este año no se cuenta con el sector {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def GENERICA(self,opcion = '', s = 'N'):#funcion para filtrar por generica
        self.encabezados[0]='Generica'#colocar nombre de selección en encabezados
        self.s = s#Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnGenerica').click() #Hacemos click en generica
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de las genericas existentes para ese año 
        if opcion in ind_lista:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.GE'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion 
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la generica ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)#Crea la tabla con los encabezados y datos 
            return solo_f#Devuelve la tabla solo de la fila
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1] +'.GE'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#devuelve la tabla anual
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en fila ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual 
        else:#En caso no se especifique opcion deveulve tabla vacia
            print('Para este año no se cuenta con la generica {}'.format(opcion))
            valor = pd. DataFrame()
            return valor

    def PLIEGO(self,opcion = '',s='N'):#funcion para filtrar por pliego
        self.encabezados[0]='Pliego'#colocar nombre de selección en encabezados
        self.s = s#Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnPliego').click() #Hacemos click en PLIEGO
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los identificadores existentes para la tabla 
        if opcion in ind_lista:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.PL'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion 
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en EL PLIEGO ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)#Crea la tabla con los encabezados y datos 
            return solo_f#Devuelve la tabla solo de la fila
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1] +'.PL'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#devuelve la tabla anual
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en fila ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual 
        else:#En caso no se especifique opcion devuelve tabla vacia
            print('Para este año no se cuenta con el pliego {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def FUNCION(self,opcion = '',s='N'):#funcion para filtrar por funcion
        self.encabezados[0]='Funcion'#colocar nombre de selección en encabezados
        self.s = s#Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnFuncion').click() #Hacemos click en Función
        except:
            pass
        
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.FN'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la función ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)#Crea la tabla con los encabezados y datos 
            return solo_f#Devuelve la tabla solo de la fila
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1] +'.FN'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#devuelve la tabla anual
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en fila ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla 
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual 
        else:#En caso no se especifique opcion devuelve tabla vacia
            print('Para este año no se cuenta con la generica {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
            
    def FUENTE(self,opcion = '',s='N'):#funcion para filtrar por fuente de financiamiento
        self.encabezados[0]='Fuente'#colocar nombre de selección en encabezados
        self.s = s#Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnFuenteAgregada').click() #Hacemos click en Función
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS PLIEGOS existentes para ese año 
        if opcion in ind_lista:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.FF'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la fila...
            solo_f = pd.DataFrame(self.VALORES('F'),columns=self.encabezados)#Crea la tabla con los encabezados y datos
            return solo_f#Devuelve la tabla solo de la fila
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1]+'.FF'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#devuelve la tabla anual
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en fila ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla 
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual 
        else:#En caso no se especifique opcion devuelve tabla vacia
            print('Para este año no se cuenta con la Fuente {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
      
    def RUBRO(self,opcion = '',s='N'):#funcion para filtrar por rubro
        self.encabezados[0]='Rubro'#colocar nombre de selección en encabezados
        self.s = s#Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnRubro').click() #Hacemos click en Rubro
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS RUBROS existentes para ese año 
        if opcion in ind_lista:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.RB'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la fila ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns=self.encabezados)#arma la tabla con los datos de la fila seleccionada
            return solo_f#Devuelve la tabla solo de la fila
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1]+'.RB'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#devuelve la tabla anual
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en cada fila ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla 
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual 
        else:#En caso no se especifique opcion devuelve tabla vacia
            print('Para este año no se cuenta con el rubro {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
        
        
    def DEPARTAMENTO(self,opcion = '',s='N'):#funcion para filtrar por departamento
        self.encabezados[0]='Departamento' #colocar nombre de selección en encabezados
        self.s = s #Si quiere código de rastreo de botones (qué botones anteriores se han presionado)
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnDepartamentoMeta').click() #Hacemos click en departamento
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS DEPARTAMENTOS existentes para ese año 
        if opcion in ind_lista:#Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.DP'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion)#Busca la posicion del boton en la lista indice
            self.pos = pos#Guarda la posicion
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en la fila ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)#arma la tabla con los datos de la fila seleccionada
            return solo_f#Devuelve la tabla solo de la fila
        elif opcion == 'TODO_A':#Caso en el que se quiere extraer toda la tabla observable 
            self.pas = self.pas.split('.')[-1]+'.DP'#Agrega el nombre del boton al historial
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados)#Crea la tabla
            return anual#devuelve la tabla anual
        elif opcion == 'TODO_M':#Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en cada fila ...
                if x == 0:#Extrae la primera tabla 
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos las tablas
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual
        else:#En caso no se especifique opcion devuelve tabla vacia
            print('Para este año no se cuenta con el departamento {}'.format(opcion))
            valor = pd. DataFrame()
            return valor
    
    def click_espera(self,xpath=''): #Funcion para que espere a la aparición de un elemento
        while True: #Mientras True
            try: #Intenta encontrar este elemento 
                self.browser.find_element_by_xpath(xpath) 
                return True #Devuelve true
            except NoSuchElementException: #En caso de excepción 
                continue #Continuar
        

    def PROYECTO(self,opcion = '',sect = '01', s='N'):#funcion para filtrar proyectos 
        antes = [self.encabezados[0]] #Extrae el primer encabezado de filtro anterior 
        new_head = self.encabezados #Guarda los encabezados en nueva variable 
        new_head[0]='Proyecto' #Cambia el primer encabezado 
        self.headings = ['CUI'] + new_head + antes #Agrega columna y une los encabezados 
        self.s = s #Opción para mostrar registro histórico 
        
        try:#Hacemos click en proyecto  
            if int(self.numero) >= 2012: #Si el año es mayor a 2012 busca el boton 
                self.browser.find_element_by_name('ctl00$CPH1$BtnProdProy').click()
            elif int(self.numero) < 2012:#Si el año es menor a 2012 busca el boton 
                self.browser.find_element_by_name('ctl00$CPH1$BtnActProy').click()
        except: #En caso no se encuentre ningún botón pasar  
            pass
        time.sleep(1) #Espera un tiempo de carga 
        try: #Si encuentra que hay más de una página seleccionar el numero 
            total = int(self.browser.find_element_by_xpath('//*[@id="ctl00_CPH1_Pager1_LblPageCount"]').text)
        except: #Si solo hay una pgina el total sera uno 
            total = 1
        if opcion == 'TODO_A': #Opción para extraer todos los proyectos 
            self.pas = self.pas.split('.')[-1]+'.PRY' #Guarda seleccion de botón en registro  
            pagina =1 #Define inicio de pagina 
            contenedor = self.DESC_PROY(sect) #Guarda la primera página 
            while total > pagina: #Si hay más páginas extraer siguientes tablas 
                time.sleep(1)
                #Click en siguiente
                #Espera a que aparezca el boton siguiente
                self.browser.find_element_by_xpath('//*[@id="ctl00_CPH1_Pager1_BtnNext"]').click()
                time.sleep(5)
                #Une la tabla de hoja 1 con las siguientes hojas 
                contenedor = contenedor.append(self.DESC_PROY(sect))
                pagina = pagina + 1 #Aumenta el contador 
            anual = contenedor #Cambiamos de nombre a la tabla 
            anual.columns= self.headings    #Cambiamos las columnas a la tabla      
            return anual #Devuelve la tabla de proyectos 
        else: #En caso no haya opción reconocible devuelve tabla vacía 
            print('Para este año no se cuenta con el Proyecto {}'.format(opcion))
            valor = pd. DataFrame() 
            return valor#Devuelve tabla vacia 
            
    def MES(self,opcion = '',s='N'):#funcion para filtrar por mes 
        self.encabezados[0]='Mes' #colocar nombre de selección en cabezados
        self.s = s #Opción para mostrar registro de botones seleccionados 
        try:
            self.browser.find_element_by_name('ctl00$CPH1$BtnMes').click() #Hacemos click en mes
        except:
            pass
        ind_lista = self.indices() #guarda en una lista los códigos de LOS MESES existentes para ese año 
        if opcion in ind_lista: #Extrae valores de fila específica
            self.pas = self.pas.split('.')[-1]+ '.MES'+opcion#Agrega seleccion al historial
            pos = ind_lista.index(opcion) #Busca la posicion del boton en la lista indice 
            self.pos = pos #Guarda pósición en una variable que puede ser referenciada en otra función 
            self.browser.find_element_by_id("tr{}".format(pos)).click() #Click en el mes ...
            solo_f = pd.DataFrame(self.VALORES('F'),columns= self.encabezados)#Crea la tabla 
            return solo_f#Devuelve la tabla solo del mes 
        elif opcion == 'TODO_A': #Caso en el que se quiere extraer la tabla observable 
            self.pas = self.pas.split('.')[-1]+'.MES' #Guarda registro de boton seleccionado 
            anual = pd.DataFrame(self.VALORES(),columns= self.encabezados) #Crea tabla 
            return anual#Devuelve tabla anual 
        elif opcion == 'TODO_M': #Caso en el que se quieren extraer los datos mensuales de toda la tabla observable
            for x,y in zip(range(0,len(ind_lista)),ind_lista):
                self.browser.find_element_by_id("tr{}".format(x)).click() #Click en fila ...
                if x == 0:#Extrae la primera tabla
                    mensual = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                elif x > 0:#Extrae las siguientes tablas y las une al anterior
                    mensual_1 = pd.DataFrame(self.VALORES('M'), columns = ['mes','dev_{}'.format(y),'gir_{}'.format(y)])
                    mensual = mensual.merge(mensual_1,how="outer",on="mes")#Unimos la tabla de todos los departamentos
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual = mensual.sort_values('mes')
            return mensual#Devuelve la tabla mensual
        else:#En caso no haya opción reconocible devuelve tabla vacía 
            print('Para este año no se cuenta con el mes {}'.format(opcion))
            valor = pd. DataFrame()
            return valor#Devuelve tabla vacia
            
    def PASADO(self,pasado='S'): #Funcion que define variables que pueden ser referenciadas en otras funciones 
        #Sirve para la creación de tablas con registro histórico
        if pasado == 'S': 
            self.s = 'S' #Caso en el que aparece registro histórico 
        elif pasado == 'N': 
            self.s = 'N' #Caso en el que no se requiere registro histórico 
        elif pasado == 'R':
            self.pas = '' #Otro caso 
            
    def DESC_PROY(self,sect = '01'):#Función para extraer datos de proyectos 
        #Por su cantidad de filas es diferente a la función de creación de tablas lineas abajo 
        datos = self.PAGINA() #Extrae el código html 
        prueba = datos.findAll("table", {"class": "Data"})[0].findAll('tr') #Encuentra la tabla de datos y sus filas 
        if len(prueba)>=1: #Si la tabla proyectos tiene filas 
            contenido = [] #Crea un contenedor para guardar los datos 
            for g in range(0,len(prueba)): #Bucle para cada fila 
                columnas = prueba[g].findAll('td') #encuentra los elementos de cada fila 
                contenedor = [columnas[x].get_text().replace('\n','').replace(',','') if x>1 else 
                              columnas[x].get_text().replace('\n','')
                              for x in range(0,len(columnas))] #Extrae los datos de cada fila quitando comas 
                if int(self.numero) >= 2012: #Si el año es mayor igual a 2012
                    #Transforma a millones los datos PIA PIM CERTIFICACION_AN COMPROMISO_AN (MENSUALES) DEVENGADO Y GIRADO
                    contenedor[2:9] = [0 if x != x or x == '' else int(x)/1000000 for x in contenedor[2:9]]
                elif int(self.numero) < 2012:#Si el año es menor igual a 2012
                    #Transforma a millones los datos PIA PIM COMPROMISO_AN (MENSUALES) DEVENGADO Y GIRADO
                    contenedor[2:7] = [0 if x != x or x == '' else int(x)/1000000 for x in contenedor[2:7]]
                contenido.append(contenedor) #Guarda datos extraídos en lista 
            tabla = pd.DataFrame(contenido)#Tranforma datos almacenados a tabla 
           #Selecciona solo los que tienen codigo unico
            tabla = tabla[tabla[1].isnull()==False] #True si es nulo y quedate con los que no lo sean 
            tabla = tabla.drop([0],axis=1) #Elimina primera columna vacía 
            tabla[['A','B']] = tabla[1].str.split(':', 1, expand=True) #separa columna en dos (CUI, NOMBRE)
            tabla = tabla.reset_index(drop=True) #vuelve al índice por default
            if int(self.numero) >= 2012: #si año es mayor igual a 2012
                tabla = tabla[['A','B',2,3,7,8]] #Extrae estas columnas 
            elif int(self.numero) < 2012: #si año es menor a 2012
                tabla = tabla[['A','B',2,3,5,6]] #Extrae estas columnas
            tabla['SECTOR'] = sect #Agrega una columna con el codigo de sector, funcion, etc. 
            tabla['A'] = tabla['A'].str.replace(' ','') #Reemplaza todos los espacion vacíos 
            tabla['B'] = tabla['B'].str.strip() #Quita espacios vacíos al comienzo y final
            return tabla #Devuelve tabla de datos 
        else: #Si la tabla proyectos no tiene fila 
            tabla = pd.DataFrame(columns=['A','B',2,3,7,8,9]) #Crea tabla vacía 
            return tabla #Devuelve tabla vacía        
            
    def PAGINA(self): #Función para extraer código html legible 
        d = self.browser.page_source #Extrae código html como objeto no manipulable 
        datos = BeautifulSoup(d,'lxml') #Transforma el objeto html en objeto manipulable (se hace legible)
        return datos#Devuelve el código html legible 
            
    def VALORES(self,y='A'):#Funcion que extrae valores anuales y mensuales para todos los casos menos proyectos 
                                 
        if y == 'A': #Si la opción es descarga anual 
            tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
            fila = tabla.find_elements_by_tag_name('tr') #selecciona filas de tabla 
            contenido = []#Crea contenedor de datos 
            for g in range(0,len(fila)): #Itera para cada fila 
                contenedor = []#Crea contenedor 2 de datos  
                if self.s == 'S':#Si la opción es con seguimiento 
                    #Extrae el nombre de la fila y le agrega el registro histórico 
                    contenedor.append('{}'.format(self.pas)+fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0])
                elif self.s == 'N':#Si la opción es sin seguimiento 
                    #Extrae el nombre de la fila
                    contenedor.append(fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0])
                if int(self.numero) >= 2012: #Si el año seleccionado es mayor igual a 2012 
                    #Extrae datos de columnas 
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,7,8]]
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato #Une nombre con datos 
                elif int(self.numero) < 2012:#Si el año seleccionado es menor a 2012 
                    #Extrae datos de columnas 
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,5,6]]
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato #une nombre con datos 
                contenido.append(contenedor) #guarda la lista de datos en otra lista (indispensable para la creación de DataFrames) 
                
        elif y == 'F': #Extrae los valores de la fila 
            tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
            fila = tabla.find_elements_by_tag_name('tr')# seleccionamos la filas
            contenido = [] #Crea contenedor vacia para almacenar listas
            g= self.pos #Guarda la posición de la variable 
            contenedor = [] #Crea contenedor 2 para alamacenar datos 
            if self.s == 'S': #Si la opción de nombre es con seguimiento histórico 
                #Coloca el registro histórico como nombre
                contenedor.append('{}'.format(self.pas)) #Extrae el nombre
            else:#Si la opción de nombre es sin seguimiento histórico 
                #Extrae el nombre de la fila de datos 
                contenedor.append(fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0])
            if int(self.numero) >= 2012:#Si el año seleccionado es mayor igual a 2012 
                #Extrae datos de columnas
                dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,7,8]]
                #Transforma datos a millones 
                dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                contenedor = contenedor + dato#une nombre con datos
            elif int(self.numero) < 2012:#Si el año seleccionado es menor a 2012 
                #Extrae datos de columnas
                dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [2,3,5,6]]
                #Transforma datos a millones
                dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                contenedor = contenedor + dato #une nombre con datos
            contenido.append(contenedor)#guarda la lista de datos en otra lista (indispensable para la creación de DataFrames) 
        elif y == 'M':#Si la opción es descarga mensual
            self.browser.find_element_by_name('ctl00$CPH1$BtnMes').click() #Hacemos click en mes
            tabla = self.browser.find_element_by_xpath('//*[@id="PnlData"]/table[2]') # seleccionamos la tabla de datos
            fila = tabla.find_elements_by_tag_name('tr')# seleccionamos la filas
            contenido = []#Crea contenedor vacia para almacenar listas
            for g in range(0,len(fila)):#itera para cada fila 
                contenedor = []#Crea contenedor 2 para alamacenar datos 
                #Extrae el numero del mes
                contenedor.append(fila[g].find_elements_by_tag_name('td')[1].text.split(':')[0] + '/{}'.format(self.numero))
                if int(self.numero) >= 2012: #Si el año seleccionado es mayor igual a 2012
                    #Extrae datos de columnas
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"") for u in [7,8]]
                    #Transforma datos a millones
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato #une nombre con datos
                elif int(self.numero) < 2012:#Si el año seleccionado es menor a 2012 
                    #Extrae datos de columnas
                    dato = [fila[g].find_elements_by_tag_name('td')[u].text.replace(',',"")for u in [5,6]]
                    #Transforma datos a millones
                    dato = [0 if x != x or x == '' else int(x)/1000000 for x in dato]
                    contenedor = contenedor + dato #une nombre con datos
                contenido.append(contenedor) #guarda la lista de datos en otra lista (indispensable para la creación de DataFrames) 
            self.retroceder() #Volver a la tabla anterior 
        return contenido #Devuelve lista con datos
    
    def CERRAR(self): #Función para cerrar el navegador 
        self.browser.quit()#Cierra sesión 
        print('Has cerrado sesión')
        
        