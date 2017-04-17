import re

from webextractors.archi.extractor import Extractor
from webextractors.tools.htmlcleaner import clean_html_string


class LCScraper(Extractor):
    def __init__(self):
        super().__init__()

    def extract_url(self, url, params):
        return self.get_data_from_ad(url, params)

    def get_data_from_ad(self, url_ad, data_base):
        dict_name_mapping = {
            'Année :': 'year',
            'Boîte de vitesse :': 'gearbox',
            'Couleur extérieure :': 'extern_color',
            'Couleur intérieure :': 'inter_color',
            'Garantie :': 'garanty',
            'Kilométrage :': 'km',
            'Mise en circulation :': 'release_date',
            'Nombre de portes :': 'door_number',
            'Puissance din :': 'power',
            'Puissance fiscale :': 'tax_power',
            'Énergie :': 'type',
            'Première main :': "first_hand",
            'Provenance :': "come_from"
        }
        try:
            soup = self.get_soup(url_ad)
            # Main Infos
            main_infos = soup.find(class_="mainInfos")
            main_name = main_infos.find(class_="iophfzp")
            name_model = main_name.find("span").text.strip()  # Keep
            main_description = main_name.find(class_="ofezhez").text  # Keep
            km_year = main_infos.find(class_="title3Detail").text
            km = int(clean_html_string(km_year.split(" - ")[0]).replace(" km", "").replace(" ", ""))  # Keep
            year = int(km_year.split(" - ")[1])  # Keep
            price = int(
                clean_html_string(main_infos.find(class_="floatR").find(class_="gpfzj").text).replace("€", "").replace(
                    " ", ""))
            dept = soup.find(class_="mB10 f14").text
            infos_box = soup.find(class_="box infosGen")

            # Car caracteristics

            infos = {dict_name_mapping[clean_html_string(name.text)]: clean_html_string(value.text) for name, value in
                     zip(infos_box.findAll('h4'), infos_box.findAll('p'))}

            conso = clean_html_string(soup.find(id="consomixte").text.replace(soup.find(id="consomixte").h3.text, ""))
            options_box = soup.find(class_="box boxOptions")
            options = [clean_html_string(elt.text) for elt in options_box.findAll("li")]

            # Concat all dictionnaries
            final_dict = {
                "model_name": name_model,
                "main_description": main_description,
                "km": km,
                "year": year,
                "price": price,
                "dept": dept,
                "trunk_size": clean_html_string(
                    soup.find(class_="VolumeCoffre").find(class_="sousTitre").find(class_="valueCoffre").text),
                "options": [elt for elt in options if len(elt) > 2],
                "consommation": conso,
                "_id": re.search("-annonce-([0-9]+)\.html", url_ad).group(1)
            }

            final_dict.update(infos)
            final_dict.update(data_base)
            return final_dict
        except Exception as e:
            print(e)
            pass
        return None
