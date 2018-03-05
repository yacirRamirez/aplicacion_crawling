import scrapy
from bs4 import BeautifulSoup
import urlparse
import json
import re
import urllib2


class SpiderProfesores(scrapy.Spider):
    name = "spiderProfesores"
    allowed_domains = ['uniandes.edu.co']
    def start_requests(self):
        urls = [
        'http://www.uniandes.edu.co'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    #### La siguiente funcion saca los departamentos de toda la universidad
    ####    -parametros:
    ####        soup: html de la pagina donde se pretende sacar los departamentos
    def sacarDepartamentos(self,soup):
        departamentos={}
        for tag in soup.find_all("a", string=re.compile("Ver departamento")):
            departamentos[tag['href']]=soup.find("a", href=re.compile(tag['href'])).string
        return departamentos

    #### La siguiente funcion saca las facultades de toda la universidad
    ####    -parametros:
    ####        soup: html de la pagina donde se pretende sacar las facultades
    def sacarFacultades(self,soup):
        facultades={}
        for tag in soup.find_all("a", string=re.compile("Ver facultad")):
            if soup.find("a", href=re.compile(tag['href'])) is not None:
                facultades[tag['href']]=soup.find("a", href=re.compile(tag['href'])).string
        return facultades

    #### Funcion que captura la pagina que se ha cargado en la varibale response para seguir navegando a
    #### otras paginas y sacar informacion de ellas
    def parse(self, response):
        url=response.url
        print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPASO POR= %s' % url)
        #### inicializaremos la sopa de tags de html que trae el response
        soup=BeautifulSoup(response.body,'html.parser')
        #### el siguiente codigo saca todos los departamentos de la universidad y entra en estos
        if not len(soup.select('a[href*="lista-departamentos"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="lista-departamentos"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
                d= self.sacarDepartamentos(BeautifulSoup(response.body,'html.parser'))
                if not len(d)==0:
                    with open('departamentos.json', 'w') as f:
                        json.dump(d, f)
                for departamento in d.keys():
                        yield scrapy.Request(url=departamento, callback=self.parse)
            except Exception as e:
                raise
            try:
                pass
                #next_page='https://sistemas.uniandes.edu.co'
                #yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        #### el siguiente codigo saca todas las facultades de la universidad y entra en estas
        if not len(soup.select('a[href*="lista-facultades"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="lista-facultades"]')[0]['href'])
            try:
                self.sacarFacultades(BeautifulSoup(response.body,'html.parser'))
                f= yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise

        #### el siguiente codigo entra a las paginas de los profesores
        if not len(soup.select('a[href*="profesor"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="profesor"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="planta"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="planta"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="catedra"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="catedra"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="nuestro-equipo"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="nuestro-equipo"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="empleado"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="empleado"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="coordinador"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="coordinador"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="personal"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="personal"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise

        #### el siguiente codigo saca informacion de los profesores de los departamentos de ciencias sociales
        if not len(soup.findAll('div', attrs={'class':re.compile('teaser-title')}))==0:
            for i,j in zip(soup.findAll('div', attrs={'class':re.compile('teaser-title')}),soup.findAll('div', attrs={'class':'cover boxcaption'})):
                enlace=''
                try:
                    enlace=urlparse.urljoin(response.url,i.find('a')['href'])
                except Exception as e:
                    pass
                nombre=''
                try:
                    nombre=i.find('a').string.strip()
                except Exception as e:
                    pass
                with open('departamentos.json', 'r') as f:
                    departamentos = json.load(f)
                departamento=departamentos['https://'+url.split('/')[2]+'/']
                puesto=''
                mail=''
                extension=''
                oficina=''
                try:
                    # la siguiente variable contiene la informacion del profesor en un arreglo de strings
                    InfoProfesor=j.find('div', attrs={'class': 'teaser-text'}).getText().split('\n')
                    puesto =InfoProfesor[0].strip()
                    mail=[ss for ss in InfoProfesor if 'uniandes' in ss][0].strip()
                    extension=[ss for ss in InfoProfesor if 'Ext' in ss][0].strip()
                    oficina=[ss for ss in InfoProfesor if 'Ofi' in ss][0].strip()
                except Exception as e:
                    pass

                yield{
                    'departamento':departamento,
                    'nombre': nombre,
                    'enlace': enlace,
                    'puesto':puesto,
                    'mail':mail,
                    'extension': extension,
                    'oficina': oficina,
                    }
        #### el siguiente codigo saca informacion de los profesores del departamento de sistemas
        if not len(soup.select('h3[class="name"]'))==0:
            for i,j in zip(soup.select('h3[class="name"]'),soup.select('h4[class="cargo"]')):
                enlace=''
                try:
                    enlace=i.find('a')['href']
                except Exception as e:
                    pass
                nombre=''
                try:
                    nombre=i.find('a').getText()
                except Exception as e:
                    pass
                with open('departamentos.json', 'r') as f:
                    departamentos = json.load(f)
                try:
                    departamento=departamentos['https://'+url.split('/')[2]+'/']
                except Exception as e:
                    pass
                try:
                    departamento=departamentos['https://'+url.split('/')[2]+'/es/']
                except Exception as e:
                    pass
                puesto=''
                try:
                    puesto=j.getText().strip()
                except Exception as e:
                    pass
                mail=''
                extension=''
                oficina=''
                try:
                    mail=enlace.split('/')[3]+'@uniandes.edu.co'
                except Exception as e:
                    pass
                yield{
                    'departamento':departamento,
                    'nombre': nombre,
                    'enlace': enlace,
                    'puesto':puesto,
                    'mail':mail,
                    'extension': extension,
                    'oficina': oficina,
                    }
