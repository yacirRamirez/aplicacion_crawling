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

    def sacarDepartamentos(self,soup):
        departamentos={}
        for tag in soup.find_all("a", string=re.compile("Ver departamento")):
            departamentos[tag['href']]=soup.find("a", href=re.compile(tag['href'])).string
        print(departamentos)
        return departamentos

    def sacarFacultades(self,soup):
        facultades={}
        for tag in soup.find_all("a", string=re.compile("Ver facultad")):
            if soup.find("a", href=re.compile(tag['href'])) is not None:
                facultades[tag['href']]=soup.find("a", href=re.compile(tag['href'])).string
        print(facultades)
        return facultades

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
                #next_page='https://antropologia.uniandes.edu.co'
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

        #### el siguiente codigo entra a las paginas de noticias
        if not len(soup.select('a[href*="noticias"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="noticias"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        if not len(soup.select('a[href*="eventos"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="eventos"]')[0]['href'])
            try:
                yield scrapy.Request(url=next_page, callback=self.parse)
            except Exception as e:
                raise
        #### el siguiente codigo entra a las paginas de los profesores
        if not len(soup.select('a[href*="profesor"]'))==0:
            next_page=urlparse.urljoin(response.url, soup.select('a[href*="profesor"]')[0]['href'])
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
        #### el siguiente codigo saca informacion de las noticias de los departamentos de ciencias sociales
        #if not len(soup.select('div[class="event"]'))==0:
        #    for i in soup.findAll('div', attrs = {'class': 'event'} ):
        #        fecha=i.find('div', attrs={'class':'day'}).string+' de '+i.find('div', attrs={'class':'month'}).string+' de '+i.find('div', attrs={'class':'year'}).string
        #        with open('departamentos.json', 'r') as f:
        #            departamentos = json.load(f)
        #        departamento=departamentos['https://'+url.split('/')[2]+'/']
        #        titulo=i.find('h2').find('a').string
        #        response2 = urllib2.urlopen(urlparse.urljoin(response.url,i.select('a[href*="noticia"]')[0]['href']))
        #        enlace= response2.url
        #        soup2=BeautifulSoup(response2.read(),'html.parser')
        #        descripcion=soup2.find('div', attrs={'id': "detail-desc"}).find('p').string
        #        yield{
        #            'departamento':departamento,
        #            'titulo': titulo,
        #            'enlace': enlace,
        #            'fecha':fecha,
        #            'descripcion':descripcion,
        #        }
            #subject_options = [i.findAll('option') for i in soup.findAll('select', attrs = {'name': 'primary_select'} )]
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
