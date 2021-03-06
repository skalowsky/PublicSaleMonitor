from typing import List
import requests
from bs4 import BeautifulSoup, Tag
from dto.link import Link

"""
This class contains all functions that provaided the tools to scraper the 'Caixa Economica Federal'
"""

URL_CAIXA = 'https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp'
URL_CAIXA_LIST = 'https://venda-imoveis.caixa.gov.br'

def getListOfLinkByState(state: str) -> List[Link]:
  """This function get all links contained on the official site, based on the provided state.
  
  Arguments:
      state {str} -- Responsible for filter the list of the link by the state.
  
  Returns:
      List[Link] -- List of link getting from the website
  """ 
  #returning the main page.
  mainPageRequest = requests.get(URL_CAIXA, verify=False)

  #converting the main page into a soup (xml).
  mainSoupPage = BeautifulSoup(mainPageRequest.text, 'html.parser')

  #returnig the new page based on main page with all links
  pageOfLinks = requests.get(buildLinkToListOfImovel(mainSoupPage, 'RS'), verify=False)

  #converting the page whit all links into a soup (xml).
  soupOfAllLinks = BeautifulSoup(pageOfLinks.text, 'html.parser')

  #filtering the 'tr' tag and putting it on a list.
  listOfLinksWithTrTag = soupOfAllLinks.find_all('tr')

  #creating the list of links which will be returned
  links:List[Link] = []

  for trTag in listOfLinksWithTrTag:
    
    link: Link = Link()
    
    for index in range(len(trTag.find_all('td'))):
      tdTag = trTag.find_all('td')[index]
      
      if isDatailTag(tdTag):
        link.link = getHRefPropertyLink(tdTag)

      if link.__validLink__():

        if isAddressTag(index):
          link.address = getTagTextDescritpion(tdTag)

        if isDistrictTag(index):
          link.district = getTagTextDescritpion(tdTag)

        if isCityTag(index):
          link.city = getTagTextDescritpion(tdTag)

        if isStateTag(index):
          link.state = getTagTextDescritpion(tdTag)

    if link.__validLink__():
      links.append(link)    

  return links

def isDatailTag(tag: Tag) -> bool:
  return tag.find('a') != None and tag.find('a').text.strip() == 'Detalhes'


def isAddressTag(index: int) -> bool:
  return index == 1


def isDistrictTag(index: int) -> bool:
  return index == 2


def isCityTag(index: int) -> bool:
  return index == 9

def isStateTag(index: int) -> bool:
  return index == 10

def getHRefPropertyLink(tdTag: Tag) -> str:
  return tdTag.find('a', href=True)['href']

def getTagTextDescritpion(tdTag: Tag) -> str:
  return tdTag.text.strip()

def buildLinkToListOfImovel(soupPage: BeautifulSoup, state: str) -> str:
  """Based on main page, this function build the link that will list all avaible imovel.
  
  Arguments:
      soupPage {BeautifulSoup} -- The main page.
      state {str} -- The state of the filter.
  
  Returns:
      str -- The link with all imovel.
  """  
  javaScriptTag = soupPage.find('script', type='text/javascript').text
  
  link = javaScriptTag[javaScriptTag.find('"'): javaScriptTag.find(',')]
  link = link.replace('"', '').replace('+', '').replace(' ', '').replace('estado', state)

  return "".join([URL_CAIXA_LIST, '/', link])