#------------------------------------------------------------------------------------------------------------------
#                             Anexo 2: Codificación del Scrapper SSI 
#------------------------------------------------------------------------------------------------------------------

import pandas as pd; #para el manejo de tablas
import numpy as np; #para el manejo de matrices 
import selenium; #paquete para web scraping dinámico 
from selenium import webdriver; #paquete para el manejo de un navegador de pruebas
from webdriver_manager.firefox import GeckoDriverManager #paquete para la descarga del navegador firefox de prueba
from selenium.webdriver.support.ui import Select; #paquete de funcionalidades del web driver 
import time # paquete para trabajar con datos tipo fecha 
from parsel import Selector #paquete para leer código HTML 
import re #paquete para leer código HTML 
from bs4 import BeautifulSoup #paquete para leer código HTML (web scraping estático)

class INVERSIONES(): #Inicia el scrapper 
    def __init__(self):
        self.browser = webdriver.Firefox(executable_path=GeckoDriverManager().install()) #Instala la versión más actual de firefox
        self.browser.get("https://ofi5.mef.gob.pe/ssi/ssi/Index") # Abre el vínculo que se desea scrappear
        self.browser.implicitly_wait(5) #Pide que de forma ímplicita se esperen 5 segundos hasta que cargue la pagina
        print("Listo! Has ingresado al SSI")
        
    def BUSCAR(self,codigo): #Función que ordena la búsqueda por código único 
        elemento = self.browser.find_element_by_id('txt_cu') #seleccionamos código único 
        elemento.clear() #Borramos cualquier contenido en la barra de búsqueda
        elemento.send_keys(codigo)#PEGAMOS EL CÓDIGO DEL PROYECTO
        #Hacemos click en buscar  
        buscar = self.browser.find_element_by_xpath('//*[@id="divContainer"]/div[1]/div[1]/div/table/tbody/tr[3]/td[1]/ul/li[1]/div/span')
        buscar.click() #Click en ícono buscar 
        time.sleep(1.2)#Pedimos que espere un tiempo de carga
        #Extrae el código HTML de la página
        pagina = self.browser.find_element_by_xpath('//*') 
        pagina = pagina.get_attribute('innerHTML') # Obtiene código html 
        self.d = BeautifulSoup(pagina,'lxml') #vuelve legible el código html 
        
        #print('Código {} hallado!'.format(codigo))
        
    def campos_tabla(self,filas,col_datos = [1,3]): 
        '''
        Función para extraer datos de tabla sin encabezados 
        '''
        #Loop para extraer los datos del proyecto
        in_f = [filas[x].findAll('td')[y].get_text().replace(',','') for y in col_datos for x in range(1,len(filas))]
        #Loop para extraer el nombre de la variable 
        encabezado = [filas[x].findAll('td')[y-1].get_text().replace('  ','') for y in col_datos for x in range(1,len(filas))]
        dato = [] #Lista vacia que sirve de contenedor de datos extraídos
        for x in in_f:
            try:
                dato.append(float(x)/1000000) #Se anexan los datos en millones de soles
            except:
                dato.append(x)
        return dato, encabezado #Se devuelve dos listas, uno con los datos y otro con los encabezados
    
    def armar_anual_mas(self,p):
        '''
        Función para extraer los datos financieros históricos y en frecuencia anual del proyecto 
        '''
        #Si no se cuenta con filas devolver una lista vacía 
        if len(p)==1:
            enc = []
            dat = []
        #Si se cuenta con filas realizar el loop
        elif len(p)>1: 
            headers = p[0].findAll('th') #Encuentra los registros con tag name "th"
            años = [p[x].findAll('td')[0].get_text() for x in range(1,len(p))] #Extrae los años 
            #Arma los encabezados para cada año
            enc = [headers[x].get_text()+"_{}".format(y) for y in años for x in range(1, len(headers)-1)]
            #Extrae los datos para cada año 
            hist = [p[y].findAll('td')[x].get_text().replace(',',"") for y in range(1,len(p)) for x in range(1,len(headers)-1)]
            #Transforma los datos en formato de número y en unidades millones
            dat = [0 if x != x or x == '' else float(x)/1000000 for x in hist]
        return dat,enc#Se devuelve dos listas, uno con los datos y otro con los encabezados
        
    def armar_mensual(self,p):
        '''
        Función para extraer el devengado mensual del proyecto 
        '''
        from datetime import datetime
        #Si no se cuenta con filas devolver una lista vacía 
        if len(p)==0:
            encabezado = []
            dato = []
        #Si se cuenta con filas, realizar el loop
        else:
            #Extrae los años
            años = [p[g].findAll('td')[0].get_text() for g in range(0,len(p))]
            #extrae los datos
            dato = [p[g].findAll('td')[u].get_text().replace(',',"") for g in range(0,len(p)) for u in range(1,13)]
            #Transforma datos en millones
            dato = [0 if x != x or x == '' else float(x)/1000000 for x in dato]
            #Lista para armar las fechas 
            meses = ['01','02','03','04','05','06','07','08','09','10','11','12']
            #Asignamos el formato fecha a cada mes de cada año 
            fecha = ['01/{}/{}'.format(y,x) for x in años for y in meses]
            #Las fechas mensuales son los encabezados 
            encabezado = [datetime.strptime(x,'%d/%m/%Y') for x in fecha]
        return dato, encabezado#Se devuelve dos listas, uno con los datos y otro con los encabezados
    
    def tabla_seace(self,tabla,pref = ''): #función para extraer información de contrataciones 
        from datetime import datetime #librería para trabajar con fechas 
        #Si la tabla esta vacía devolver una lista vacía 
        if len(tabla)==0: 
            heading=[]
            dato = []
        #Si se cuenta con filas, realizar el loop
        else: 
            #Encabezados de la tabla 
            nombres = ['Descripcion_','Contratista_', 'Contrato_', 'Suscripcion_', 'Monto total_', 'Monto item_']
            #Encabezados con identificadores Ob_Descripcion_1 (Descripcion de la primera obra) y así sucesivamente
            heading = ['{}'.format(pref)+x+'{}'. format(y) for y in range(1,len(tabla)+1) for x in nombres]
            #Extraer los datos 
            dato = [float(tabla[x].findAll('td')[y].get_text().replace(',',''))/1000000 if y ==5 or y==6 
                     else datetime.strptime(tabla[x].findAll('td')[y].get_text(),'%d/%m/%Y').date() if y == 4 else 
                     tabla[x].findAll('td')[y].get_text() for x in range(0,len(tabla)) for y in range(1,7)]
        return dato, heading#Se devuelve dos listas, uno con los datos y otro con los encabezados

    def GENERAL(self): #función para extraer información general 
        '''
        Función para extraer datos generales del proyecto 
        '''
        from datetime import datetime
        filas_1 = self.d.findAll('tbody')[2].findAll('tr') #infromacion general 
        filas_2 = self.d.findAll('tbody')[3].findAll('tr') #institucionalidad 
        filas_3 = self.d.findAll('tbody')[4].findAll('tr') #formulacion y evaluacion 
        filas_4 = self.d.findAll('tbody')[5].findAll('tr') #ejecucion 
        
        encabezados = [filas_1[x].findAll('td')[0].get_text() for x in range(3)] #extrae encabezados de informacion general 
        encabezados.append(filas_2[3].findAll('td')[0].get_text()) #encabezado de unidad ejecutora 
        head = [filas_3[x].findAll('td')[2].get_text() for x in range(1,4)] #extrae encabezados de formulacion y evaluacion 
        ejec_e = [filas_4[x].findAll('td')[y].get_text() for x,y in zip(range(1,5),[2,2,2,4])] #extrae encabezados de ejecucion 
        fechas_e = [filas_4[4].findAll('td')[x].get_text() for x in [0,2]] #extrae encabezados de fechas de ejecucion 
        encabezados = encabezados + head + ejec_e + fechas_e #une los encabezados en una sola lista 
         
        datos = [filas_1[x].findAll('td')[1].get_text() for x in range(3)]#extrae datos de informacion general 
        datos.append(filas_2[3].findAll('td')[1].get_text())#extrae de unidad ejecutora 
        cuerpo = [filas_3[x].findAll('td')[3].get_text().replace(',',"") for x in range(1,4)]#extrae datos de formulacion y evaluacion 
        
        if cuerpo[0] != cuerpo[0] or cuerpo[0]=='':#Si la primera celda esta vacía 
            p1=[0]                                 #p1 será cero 
        else:                                       #Si no está vacía
            p1 = [datetime.strptime(cuerpo[0],'%d/%m/%Y')] #p1 será fecha 
        
        p2 = [0 if x != x or x == '' else float(x)/1000000 for x in cuerpo[1:]] #Transforma los datos a millones 
        
        formu = p1+p2 #Unimos los datos de formulacion y evaluacion 
        ejec = [filas_4[x].findAll('td')[y].get_text().replace(',',"") for x,y in zip(range(1,5),[3,3,3,5])] #extrae datos de ejecucion
        ejec = [0 if x != x or x == '' else float(x)/1000000 for x in ejec] #Transforma los datos a millones
        fechas = [filas_4[4].findAll('td')[x].get_text() for x in [1,3]]#extrae datos de fechas de ejecucion 
        fechas = [0 if x != x or x == '' else datetime.strptime(x,'%d/%m/%Y') for x in fechas] #Transforma los datos a fecha 
        datos = [datos + formu + ejec + fechas]                          #une los datos en una sola lista 

        tabla = pd.DataFrame(datos,columns=encabezados) #Crea el Dataframe 
        
        return tabla #Devuelve como respuesta la tabla creada
    
    def SIAF(self):
        '''
        Función para extraer datos financieros del proyecto 
        '''
        filas_0 = self.d.findAll('tbody')[2].findAll('tr')#Extrae código unico
        filas_1 = self.d.findAll('tbody')[9].findAll('tr') #Información financiera
        filas_2 = self.d.findAll('table')[10].findAll('tr') #Devengado histórico anual
        filas_3 = self.d.findAll('tbody')[13].findAll('tr') #por especifica
        filas_4 = self.d.findAll('tbody')[5].findAll('tr') # por unidad ejecutora
        filas_5 = self.d.find("tbody", {"id": "tb_devmes"}).findAll('tr') # devengado mensual
        
        cod = [filas_0[0].findAll('td')[1].get_text()] #codigo unico
        dat,enc = self.campos_tabla(filas_1,[1,3])#Información financiera (dato,encabezados)
        dat1,enc1 = self.armar_anual_mas(filas_2) #Devengado anual(dato,encabezados)
        dat2,enc2 = self.armar_mensual(filas_5) #Devengado mensual(dato,encabezados)
       
        datos = [cod+dat+dat1+dat2] #Une las listas de datos 
        
        cod_e = [filas_0[0].findAll('td')[0].get_text()] #Extrae el encabezado de codigo unico 
        encabezados =cod_e+enc+enc1+enc2 #Une la lista de encabezados 
        
        tabla = pd.DataFrame(datos,columns=encabezados) #crea la tabla con los datos y encabezados 
        return tabla #Devuelve como respuesta la tabla creada
    
    def SEACE(self):
        '''
        Función para extraer datos de contrataciones del proyecto 
        '''
        time.sleep(1) #ordena que espere un tiempo de carga 
        pagina = self.browser.page_source #Obtiene el codigo html 
        self.d = BeautifulSoup(pagina,'lxml') #devuelve el codigo html legible 
        
        filas_0 = self.d.findAll('tbody')[2].findAll('tr') #Código único
        filas_1 = self.d.find("tbody", {"id": "tb_seaceobra"}).findAll('tr')#Tabla de obras
        filas_2 = self.d.find("tbody", {"id": "tb_seaceserv"}).findAll('tr')#Tabla de servicios 
        filas_3 = self.d.find("tbody", {"id": "tb_seaceconsul"}).findAll('tr')#Tabla de consultorias 
        
        cod = [filas_0[0].findAll('td')[1].get_text()] #codigo unico
        dat,enc = self.tabla_seace(filas_1,'Ob_') #obtiene dato de obras (dato,encabezados)
        dat1,enc1 = self.tabla_seace(filas_2,'Serv_') #obtiene dato de servicios (dato,encabezados) 
        dat2,enc2 = self.tabla_seace(filas_3,'Consul_') #obtiene dato de servicios (dato,encabezados)
        
        datos = [cod+dat+dat1+dat2] #une los datos en una sola lsita 
        
        cod_e = [filas_0[0].findAll('td')[0].get_text()] #Extrae el encabezado de codigo unico 
        encabezados =cod_e+enc+enc1+enc2 #une los encabezados en una lista 
        
        tabla = pd.DataFrame(datos,columns=encabezados) #crea la tabla con los datos y encabezados 
        return tabla#Devuelve como respuesta la tabla creada
    
    def COMPLETO(self):
        '''
        Función para extraer todos los datos del proyecto 
        '''
        gen = self.GENERAL() #Aplica dentro de la clase la función para obtener tabla de datos generales 
        ejec = self.SIAF() #Aplica dentro de la clase la función para obtener tabla de datos financieros 
        cont = self.SEACE() #Aplica dentro de la clase la función para obtener tabla de contrataciones
        #une tablas en base al código único 
        tabl = gen.merge(cont,how = 'outer', on = 'CÓDIGO ÚNICO') #Une tabla gen con tabla cont
        tabla = tabl.merge(ejec,how = 'outer', on = 'CÓDIGO ÚNICO') #une tabla anterior con tabla ejec
        
        return tabla  #Devuelve la tabla unida
        
    def CERRAR(self): #Función para cerrar sesión 
        self.browser.quit() #Cierra el navegador y termina la sesión
        print('Has cerrado sesión')