"""
Module to interact with knowledge graph
"""
from ER.Entity import Entity
from ER.Patient import Patient
from ER.Relationship import Relationship
from db_services.neo4j_services import matchP, matchPRE, matchPR, matchPE, matchRE, involve_info
from nlp.ERextractor import ER_extractor
from datetime import datetime


def verifyInfo(doc):
    now = datetime.now()

    current_date = now.strftime("%d/%m/20%y")
    BN_list, triplets = ER_extractor(doc, current_date)
    bn_verify = 1
    re_verify = 1

    patients = []
    relationships = []
    entities = []

    for bn in BN_list:
        p = Patient()
        p.name = bn[0]
        p.age = bn[1]
        p.gender = bn[2]
        p.home_town = bn[3]
        p.country = bn[4]
        patients.append(p)
        if check_patient(p) is False:
            bn_verify = 0

    for triplet in triplets:
        p = Patient()
        e = Entity()
        r = Relationship()

        p.name = triplet[0][0]
        r.label = triplet[1][0].replace(" ", "_")

        e.name = triplet[2][0]
        e.label = triplet[2][1]
        patients.append(p)
        relationships.append(r)
        entities.append(e)
        if re_verify != 2 and matchPRE(p, r, e):
            if re_verify == 0:
                continue
            re_verify = 1  # thong tin xac thuc
        else:
            if re_verify == 0:
                continue
            if (matchPR(p, r) or matchPE(p, e) or matchRE(r, e)):
                re_verify = 0  # thong tin chua duoc xac thuc
            else:
                re_verify = 2  # không đủ thông tin để xác thực

    if not BN_list or not triplets:
        re_verify = 2
    if bn_verify == 0:
        verify = 0
    else:
            verify = re_verify

    visualization = involve_info(patients, relationships, entities)
    data = {
        "verify": verify,
        "visualization": visualization
    }
    return data


def check_patient(p):
    pcheck = matchP(p)
    if p.age != None and p.age != pcheck['age']:
        return False
    if p.gender != None and p.gender != pcheck['gender']:
        return False
    if p.country != None and p.country != pcheck['country']:
        return False
    if p.home_town != None and p.home_town != pcheck['home_town']:
        return False
    return True
