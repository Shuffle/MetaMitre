from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from flask import Request
from ioc_finder import find_iocs

import os
import sys
import getopt
import joblib
import json
import time
import uuid
from shutil import copyfile
from colorama import init, Fore, Back, Style
from operator import itemgetter

import classification_tools.preprocessing as prp
import classification_tools.postprocessing as pop
import classification_tools.save_results as sr
import classification_tools as clt

import nltk
nltk.download('punkt')
nltk.download('wordnet')

parameters = joblib.load("classification_tools/data/configuration.joblib")
#if __name__ != "__main__":
#    parameters = joblib.load("gs://classification_tools/data/configuration.joblib")

min_prob_tactics = parameters[2][0]	
max_prob_tactics = parameters[2][1]
min_prob_techniques = parameters[3][0]
max_prob_techniques = parameters[3][1]

def get_result(data):
    global parameters

    start = time.time()
    #print(f"Running data of length: {len(data)}")
    analysis_id = str(uuid.uuid4())
    ttps = {
        "success": True,
        "timing": {
            "analysis_time": -1,
            "time_variant": "seconds",
        },
        "input_length": len(data),
        "tactics_checked": 0,
        "techniques_checked": 0,
        "tactics": [],
        "techniques": [],
        "analysis_id": analysis_id,
    }


    #with open(report_to_predict_file, 'r', newline = '', encoding = 'ISO-8859-1') as filetoread:
    #data = filetoread.read()
    report_to_predict = prp.remove_u(data)
    
    # load postprocessingand min-max confidence score for both tactics and techniques predictions

    pred_tactics, predprob_tactics, pred_techniques, predprob_techniques = clt.predict(report_to_predict, parameters)

    # change decision value into confidence score to display
    for i in range(len(predprob_tactics[0])):
        conf = (predprob_tactics[0][i] - min_prob_tactics) / (max_prob_tactics - min_prob_tactics)
        if conf < 0:
            conf = 0.0
        elif conf > 1:
            conf = 1.0
            predprob_tactics[0][i] = conf*100

    for j in range(len(predprob_techniques[0])):
        conf = (predprob_techniques[0][j] - min_prob_techniques) / (max_prob_techniques - min_prob_techniques)
        if conf < 0:
            conf = 0.0
        elif conf > 1:
            conf = 1.0
            predprob_techniques[0][j] = conf*100

    #prepare results to display
    to_print_tactics = []
    to_print_techniques = []
    for ta in range(len(pred_tactics[0])):
        ttps["tactics_checked"] += 1
        if pred_tactics[0][ta] == 1:
            ttps["tactics"].append({
                "code": clt.CODE_TACTICS[ta],
                "confidence": float("{:.2%}".format(predprob_tactics[0][ta])[:-1]),
                "confidence_variant": "percent",
            })
            #"confidence": 

            to_print_tactics.append([1, clt.NAME_TACTICS[ta], predprob_tactics[0][ta]])
        else:
            to_print_tactics.append([0, clt.NAME_TACTICS[ta], predprob_tactics[0][ta]])

    for te in range(len(pred_techniques[0])):
        ttps["techniques_checked"] += 1
        if pred_techniques[0][te] == 1:
            ttps["techniques"].append({
                "code": clt.CODE_TECHNIQUES[te],
                "confidence": float("{:.2%}".format(predprob_techniques[0][te])[:-1]),
                "confidence_variant": "percent",
            })

            to_print_techniques.append([1, clt.NAME_TECHNIQUES[te], predprob_techniques[0][te]])
        else:
            to_print_techniques.append([0, clt.NAME_TECHNIQUES[te], predprob_techniques[0][te]])

    to_print_tactics = sorted(to_print_tactics, key = itemgetter(2), reverse = True)
    to_print_techniques = sorted(to_print_techniques, key = itemgetter(2), reverse = True)

    #print(f"\n\nPredictions for the given report of length {len(data)} are : ")
    #print("Tactics:")
    #for tpta in to_print_tactics:
    #    if tpta[0] == 1:
    #        print(Fore.YELLOW + '' + tpta[1] + " : " + str(tpta[2]) + "% confidence")
    #    else:
    #        print(Fore.CYAN + '' + tpta[1] + " : " + str(tpta[2]) + "% confidence")

    #print(Style.RESET_ALL)
    #print("Techniques :")
    #for tpte in to_print_techniques:
    #    if tpte[0] == 1:
    #        print(Fore.YELLOW + '' + tpte[1] + " : "+str(tpte[2])+"% confidence")
    #    else:
    #        print(Fore.CYAN + '' + tpte[1] + " : "+str(tpte[2])+"% confidence")

    #print(Style.RESET_ALL)

    end = time.time()
    ttps["timing"]["analysis_time"] = end-start

    return ttps

def get_ioc_data(data):
    iocs = find_iocs(data)
    newarray = []
    for key, value in iocs.items():
        if len(value) > 0:
            for item in value:
                # If in here: attack techniques. Shouldn't be 3 levels so no
                # recursion necessary
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if len(subvalue) > 0:
                            for subitem in subvalue:
                                data = {
                                    "data": subitem,
                                    "data_type": "%s_%s" % (key[:-1], subkey),
                                }
                                if data not in newarray:
                                    newarray.append(data)
                else:
                    data = {"data": item, "data_type": key[:-1]}
                    if data not in newarray:
                        newarray.append(data)

    # Reformatting IP
    for item in newarray:
        if "ip" in item["data_type"]:
            item["data_type"] = "ip"
            try:
                item["is_private_ip"] = ipaddress.ip_address(item["data"]).is_private
            except:
                print("Error parsing %s" % item["data"])
                pass

    return newarray

def get_ioc_result(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        Object data with IOCs from the request
    """

    parsed_data = ""
    if isinstance(request, str): 
        parsed_data = request#["data"]
    else:
        # Super simple auth mechanism for now
        if request.headers.get("Authorization") != os.getenv("SHUFFLE_APIKEY"):
            return {
                "success": False,
                "reason": "Bad apikey. Set Authorization header.",
            }

        try:
            parsed_data = request.data
        except Exception as e:
            return {
                "success": False,
                "reason": f"ERROR in request data parsing: {e}",
            }

    try:
        parsed_data = parsed_data.decode("utf-8")
    except:
        pass

    if len(parsed_data) == 0:
        return {
            "success": False,
            "reason": f"No data to handle. Send POST request with data and content-type text/plain",
        }

    print("[INFO] Handling data of length {len(parsed_data)}")

    ret = get_ioc_data(parsed_data)

    try:
        return json.dumps(ret)
    except Exception as e:
        return {
            "success": False,
            "reason": f"Error returning data: {e}",
        }

def get_mitre_result(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        Objects from Mitre Att&ck
    """


    parsed_data = ""
    if isinstance(request, str): 
        parsed_data = request#["data"]
    else:
        # Super simple auth mechanism for now
        if request.headers.get("Authorization") != os.getenv("SHUFFLE_APIKEY"):
            return {
                "success": False,
                "reason": "Bad apikey. Set Authorization header.",
            }

        try:
            parsed_data = request.data
            #print(f"DATA: {parsed_data}")
            #parsed_data = json_data["data"]
        except Exception as e:
            return {
                "success": False,
                "reason": f"ERROR in request data parsing: {e}",
            }

    try:
        parsed_data = parsed_data.decode("utf-8")
    except:
        pass

    if len(parsed_data) == 0:
        return {
            "success": False,
            "reason": f"No data to handle. Send POST request with data and content-type text/plain",
        }

    print("[INFO] Handling data of length {len(parsed_data)}")
    ret = get_result(parsed_data)

    try:
        return json.dumps(ret)
    except Exception as e:
        return {
            "success": False,
            "reason": f"Error returning data: {e}",
        }

if __name__ == "__main__":
    #import warnings
    #warnings.warn("deprecated", DeprecationWarning)
    data = "THIS IS SOME DATA google.com 1.2.3.4"
    ret = get_ioc_result(data)
    print(ret)
