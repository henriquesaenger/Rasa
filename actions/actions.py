# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from unidecode import unidecode
from xml.etree import ElementTree
import requests





class ActionBuscarNumero(Action):

    def name(self) -> Text:
        return "ActionBuscarNumero"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city=tracker.get_slot("localidade")            #pega a cidade escolhida
        UF=tracker.get_slot("unidade")                #pega o estado da cidade
        UF=UF.upper()
        city= unidecode(city)          #tira os acentos da cidade
        city= city.replace(" ", "%20")                      #substitui os espaços por "%20" pelas regras da API
        response= requests.get("http://servicos.cptec.inpe.br/XML/listaCidades?city="+city)    #faz a requisição do número da cidade
        tree = ElementTree.fromstring(response.content)                #faz o parse desse XML
        xmlDict = {}                  #cria um dicionário para armazenar as cidades e estados do XML
        #percorre as tags enquanto forma o dicionário tendo os estados como Key e o o número ID da cidade como Value
        for sitemap in tree:
            children = sitemap.getchildren()
            xmlDict[children[1].text] = children[2].text
        id_city=xmlDict.get(UF)                          #pega no dicionário o ID da cidade escolhida pelo usuário
        responsenum= requests.get("http://servicos.cptec.inpe.br/XML/cidade/7dias/"+id_city+"/previsao.xml")
        tre = ElementTree.fromstring(responsenum.content)                #faz o parse desse XML da previsão do tempo
        texto=""
        for sitemap in tre.findall('previsao'):              #percorre o xml organizando os dias, as máximas e as mínimas em seu lugar
            dia_comp = sitemap.find('dia').text.split("-")
            dia = dia_comp[2]+"/"+ dia_comp[1]
            diaMax = sitemap.find('maxima').text
            diaMin= sitemap.find('minima').text
            texto= texto+ "Dia "+dia+":  Temp. Máxima "+ diaMax+ "  Temp Mínima "+ diaMin+"\n"
        if(tre.find('atualizacao') != None):
            atual=tre.find('atualizacao').text                  #armazena a data da última atualização do sistema
            texto= texto+ "\n Última Atualização: "+ atual
        dispatcher.utter_message(texto)
        return[]