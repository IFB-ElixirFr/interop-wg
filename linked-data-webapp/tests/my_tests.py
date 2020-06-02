import unittest
import json
import requests
from rdflib import ConjunctiveGraph, Graph


class MyTestCase(unittest.TestCase):


    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        print("STARTING all tests")

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        print("ENDING all tests")

    def test_something(self):
        d = {'microdata': [], 'json-ld': [{'@context': 'http://schema.org', '@type': 'ScholarlyArticle', '@id': 'https://doi.org/10.7892/boris.108387', 'identifier': {'@type': 'PropertyValue', 'propertyID': 'DOI', 'value': 'https://doi.org/10.7892/boris.108387'}, 'url': 'https://boris.unibe.ch/108387/', 'name': 'Diagnostic value of contrast-enhanced magnetic resonance angiography in large-vessel vasculitis.', 'author': [{'name': 'Sabine Adler', 'givenName': 'Sabine', 'familyName': 'Adler', '@type': 'Person'}, {'name': 'Marco Sprecher', 'givenName': 'Marco', 'familyName': 'Sprecher', '@type': 'Person'}, {'name': 'Felix Wermelinger', 'givenName': 'Felix', 'familyName': 'Wermelinger', '@type': 'Person'}, {'name': 'Thorsten Klink', 'givenName': 'Thorsten', 'familyName': 'Klink', '@type': 'Person'}, {'name': 'Harald Marcel Bonel', 'givenName': 'Harald Marcel', 'familyName': 'Bonel', '@type': 'Person'}, {'name': 'Peter M Villiger', 'givenName': 'Peter M', 'familyName': 'Villiger', '@type': 'Person'}], 'description': 'OBJECTIVE To evaluate contrast-enhanced magnetic resonance angiography (MRA) in diagnosis of inflammatory aortic involvement in patients with clinical suspicion of large-vessel vasculitis. PATIENTS AND METHODS Seventy-five patients, mean age 62 years (range 16-82 years), 44 female and 31 male, underwent gadolinium-enhanced MRA and were evaluated retrospectively. Thoracic MRA was performed in 32 patients, abdominal MRA in 7 patients and both thoracic and abdominal MRA in 36 patients. Temporal arterial biopsies were obtained from 22/75 patients. MRA positivity was defined as increased aortic wall signal in late gadolinium-enhanced axial turbo inversion recovery magnitude (TIRM) series. The influence of prior glucocorticoid intake on MRA outcome was evaluated. RESULTS MRA was positive in 24/75 patients, with lesions located in the thorax in 7 patients, the abdomen in 5 and in both thorax and abdomen in 12. Probability for positive MRA after glucocorticoid intake for more than 5 days before MRA was reduced by 89.3%. Histology was negative in 3/10 MRA-positive patients and positive in 5/12 MRA-negative patients. All 5/12 histology positive / MRA-negative patients had glucocorticoids for &gt;5 days prior to MRA and were diagnosed as having vasculitis. Positive predictive value for MRA was 92%, negative predictive value was 88%. CONCLUSIONS Contrast-enhanced MRA reliably identifies large vessel vasculitis. Vasculitic signals in MRA are very sensitive to glucocorticoids, suggesting that MRA should be done before glucocorticoid treatment.', 'keywords': '610 Medicine &amp; health', 'inLanguage': 'eng', 'encodingFormat': 'application/pdf', 'datePublished': '2017', 'publisher': {'@type': 'Organization', 'name': 'EMH Schweizerischer Ärzteverlag'}, 'provider': {'@type': 'Organization', 'name': 'DataCite'}}], 'rdfa': [{'@id': '_:Nf70c6201ecc34f838a5b31d5ebbff888', 'http://www.w3.org/1999/xhtml/vocab#role': [{'@id': 'http://www.w3.org/1999/xhtml/vocab#navigation'}]}]}

        d_prime = {'microdata': [], 'json-ld': [{"@context": {"@base": "https://bio.tools/", "sc": "http://schema.org/",},
                                           '@type': 'ScholarlyArticle',
                                           '@id': 'https://doi.org/10.7892/boris.108387',
                                           'identifier': {'@type': 'PropertyValue', 'propertyID': 'DOI',
                                                          'value': 'https://doi.org/10.7892/boris.108387'},
                                           'url': 'https://boris.unibe.ch/108387/',
                                           'name': 'Diagnostic value of contrast-enhanced magnetic resonance angiography in large-vessel vasculitis.',
                                           'author': [
                                               {'name': 'Sabine Adler', 'givenName': 'Sabine', 'familyName': 'Adler',
                                                '@type': 'Person'}, {'name': 'Marco Sprecher', 'givenName': 'Marco',
                                                                     'familyName': 'Sprecher', '@type': 'Person'},
                                               {'name': 'Felix Wermelinger', 'givenName': 'Felix',
                                                'familyName': 'Wermelinger', '@type': 'Person'},
                                               {'name': 'Thorsten Klink', 'givenName': 'Thorsten',
                                                'familyName': 'Klink', '@type': 'Person'},
                                               {'name': 'Harald Marcel Bonel', 'givenName': 'Harald Marcel',
                                                'familyName': 'Bonel', '@type': 'Person'},
                                               {'name': 'Peter M Villiger', 'givenName': 'Peter M',
                                                'familyName': 'Villiger', '@type': 'Person'}],
                                           'description': 'OBJECTIVE To evaluate contrast-enhanced magnetic resonance angiography (MRA) in diagnosis of inflammatory aortic involvement in patients with clinical suspicion of large-vessel vasculitis. PATIENTS AND METHODS Seventy-five patients, mean age 62 years (range 16-82 years), 44 female and 31 male, underwent gadolinium-enhanced MRA and were evaluated retrospectively. Thoracic MRA was performed in 32 patients, abdominal MRA in 7 patients and both thoracic and abdominal MRA in 36 patients. Temporal arterial biopsies were obtained from 22/75 patients. MRA positivity was defined as increased aortic wall signal in late gadolinium-enhanced axial turbo inversion recovery magnitude (TIRM) series. The influence of prior glucocorticoid intake on MRA outcome was evaluated. RESULTS MRA was positive in 24/75 patients, with lesions located in the thorax in 7 patients, the abdomen in 5 and in both thorax and abdomen in 12. Probability for positive MRA after glucocorticoid intake for more than 5 days before MRA was reduced by 89.3%. Histology was negative in 3/10 MRA-positive patients and positive in 5/12 MRA-negative patients. All 5/12 histology positive / MRA-negative patients had glucocorticoids for &gt;5 days prior to MRA and were diagnosed as having vasculitis. Positive predictive value for MRA was 92%, negative predictive value was 88%. CONCLUSIONS Contrast-enhanced MRA reliably identifies large vessel vasculitis. Vasculitic signals in MRA are very sensitive to glucocorticoids, suggesting that MRA should be done before glucocorticoid treatment.',
                                           'keywords': '610 Medicine &amp; health', 'inLanguage': 'eng',
                                           'encodingFormat': 'application/pdf', 'datePublished': '2017',
                                           'publisher': {'@type': 'Organization',
                                                         'name': 'EMH Schweizerischer Ärzteverlag'},
                                           'provider': {'@type': 'Organization', 'name': 'DataCite'}}], 'rdfa': [
            {'@id': '_:Nf70c6201ecc34f838a5b31d5ebbff888',
             'http://www.w3.org/1999/xhtml/vocab#role': [{'@id': 'http://www.w3.org/1999/xhtml/vocab#navigation'}]}]}

        s = d_prime['json-ld']
        # print(s)
        # print(s.encode())
        # print(s.encode("ascii", "ignore"))
        #
        # print(json.dumps(d))
        # print(json.dumps(d).encode())
        # print((json.dumps(d)).encode("ascii", "ignore"))
        # print((json.dumps(d)).encode("ascii", "ignore").decode())

        #print(json.dumps(d_prime))
        #print(json.dumps(d_prime, ensure_ascii=False))

        # a  = {"@id": "http://doi.org/10.7892/boris.108387"}
        # b = """
        #     {
        #         "@context": {
        #             "@language": "en",
        #             "@vocab": "http://purl.org/dc/terms/"
        #         },
        #         "@id": "http://example.org/about",
        #         "title": "Someone's Homepage"
        #     }
        # """
        # c = {
        #         "@context": {
        #             "@language": "en",
        #             "@vocab": "http://purl.org/dc/terms/"
        #         },
        #         "@id": "http://example.org/about",
        #         "title": "Someone's Homepage"
        #     }

        raw_a = json.dumps(s, indent=4, sort_keys=True)
        print(raw_a)

        mygraph = Graph()
        mygraph.parse(data=str(raw_a), format="json-ld")
        print(mygraph.serialize(format="turtle").decode())

        #kg.parse(data=json.dumps(c), format="json-ld")
        #kg.parse(data=json.dumps(a, ensure_ascii=False), format="json-ld")
        # kg.parse(data=a_second, format="json-ld")

        self.assertEqual(True, True)

    # def test_another_thing(self):
        # uri = "https://bio.tools/bwa"
        # h = {'Accept': 'text/turtle'}
        # p = {'query': "DESCRIBE <" + uri + ">"}
        # res = requests.get("https://134.158.247.76/sparql", headers = h, params=p, verify=False)
        # print(res.text)
        # kg = ConjunctiveGraph()
        # kg.parse(data=res.text, format="turtle")
        # print(len(kg))
        # print(kg.serialize(format="turtle").decode())
        #self.assertEqual(True, True)

    # def test_utf8(self):
        # data = '{"@context": "http://schema.org", "@id": "http://example.org/about"}'
        # data = data.encode("utf-8")


if __name__ == '__main__':
    unittest.main()
