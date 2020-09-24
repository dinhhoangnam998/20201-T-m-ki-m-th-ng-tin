from ER.Entity import Entity
from ER.Patient import Patient
from ER.Relationship import Relationship
from nlp.src.predict import ner_sent, load_model, ner_sent2
from nlp.src.preprocess_raw import preprocess_raw
from nlp.src.extract import extract_info
from config.config import NLPConfig

my_config = NLPConfig()
model_dir = my_config.model_path
data_dir = my_config.data_path


def ER_extractor(doc, time):
    model = load_model(model_dir + 'covid_ner_8764w.job')
    BN_list, triplets = extract_info(paragraph=doc, model=model, time_public=time)

    return BN_list, triplets
