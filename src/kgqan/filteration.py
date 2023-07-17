import os

import re
from urllib.parse import urlparse

#from nlp.models import ner
import kgqan.embeddings_client as w2v


def is_person(output):
    for tag in output["tags"]:
        if "PERSON" in tag:
            return True
    return False


def is_place(output):
    for tag in output["tags"]:
        if "GPE" in tag or "FAC" in tag or "LOC" in tag:
            return True
    return False


def is_language(output):
    for tag in output["tags"]:
        if "LANGUAGE" in tag:
            return True
    return False


def extract_resource_name_from_uri(uri: str):
    resource_URI = uri
    uri_path = urlparse(resource_URI).path
    resource_name = os.path.basename(uri_path)
    resource_name = re.sub(r"(:|_|\(|\))", " ", resource_name)
    return resource_name


# def update_results(results, answer_type):
#     filtered_bindings = []
#     if 'person' in answer_type:
#         return filter_person(results)
#     elif 'place' in answer_type:
#         return filter_place(results)
#     elif 'language' in answer_type:
#         return filter_language(results)
#     return results


def test_is_person(types):
    # if len(types) == 0:
    #     return True

    for type in types:
        # or '/Organization' in type
        if "/Person" in type:
            return True
    return False


def test_filter_person(results, types):
    filtered_bindings = []
    for i in range(len(results["bindings"])):
        # if test_is_general(types[i], ['person']):
        if test_is_person(types[i]):
            filtered_bindings.append(results["bindings"][i])

    return {"bindings": filtered_bindings}


def test_is_place(types):
    for type in types:
        if "/Place" in type or "/Location" in type:
            return True
    return False


def test_filter_place(results, types):
    filtered_bindings = []
    for i in range(len(results["bindings"])):
        # if test_is_general(types[i], ['place']):
        if test_is_place(types[i]):
            filtered_bindings.append(results["bindings"][i])

    return {"bindings": filtered_bindings}


def test_is_language(types):
    for type in types:
        if "/Language" in type:
            return True
    return False


def test_filter_language(results, types):
    filtered_bindings = []
    for i in range(len(results["bindings"])):
        # if test_is_general(types[i], ['language']):
        if test_is_language(types[i]):
            filtered_bindings.append(results["bindings"][i])

    return {"bindings": filtered_bindings}


def test_is_general(types, answer_type, knowledge_graph):
    if (
        knowledge_graph == "lc_quad"
        or knowledge_graph == "dblp"
        or knowledge_graph == "microsoft_academic"
    ):
        threshold = 0.2 if knowledge_graph == "lc_quad" else 0.5
        max_score = 0
        for type in types:
            name = extract_type_names(type)
            score = w2v.n_similarity(answer_type, [name])
            max_score = max(max_score, score)

        if max_score > threshold:
            return True
        # if '/' + answer_type[0] in type.lower():
        #     return True
        return False
    else:
        for type in types:
            if "/" + answer_type[0] in type.lower():
                return True
        return False


def test_filter_general(results, answer_type, types, knowledge_graph):
    filtered_bindings = []
    for i in range(len(results["bindings"])):
        if results["bindings"][i]["uri"]["type"] == "bnode":
            continue
        if test_is_general(types[i], answer_type, knowledge_graph):
            filtered_bindings.append(results["bindings"][i])

    return {"bindings": filtered_bindings}


def update_results(results, answer_type, types, knowledge_graph):
    if "person" in answer_type:
        return test_filter_person(results, types)
    elif "place" in answer_type:
        return test_filter_place(results, types)
    elif "language" in answer_type:
        return test_filter_language(results, types)
    elif len(answer_type) > 0 and answer_type[0] not in [
        "boolean",
        "date",
        "count",
        "other",
        "string",
        "price",
    ]:
        return test_filter_general(results, answer_type, types, knowledge_graph)
    bindings = []
    for i in range(len(results["bindings"])):
        if results["bindings"][i]["uri"]["type"] != "bnode":
            bindings.append(results["bindings"][i])
    results["bindings"] = bindings
    return results


def filter_person(results):
    filtered_bindings = []
    value = ""
    for binding in results["bindings"]:
        if (
            binding["uri"]["type"] == "typed-literal"
            and "langString" in binding["uri"]["datatype"]
        ):
            value = binding["uri"]["value"]
            allennlp_ner_output = ner.predict(sentence=value)
            if is_person(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding["uri"]["type"] == "uri":
            value = extract_resource_name_from_uri(binding["uri"]["value"])
            allennlp_ner_output = ner.predict(sentence=value)
            if is_person(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding["uri"]["type"] == "literal":
            value = binding["uri"]["value"]
            if len(value.split()) > 5:
                continue
            allennlp_ner_output = ner.predict(sentence=value)
            if is_person(allennlp_ner_output):
                filtered_bindings.append(binding)

    return {"bindings": filtered_bindings}


def filter_place(results):
    filtered_bindings = []
    value = ""
    for binding in results["bindings"]:
        if (
            binding["uri"]["type"] == "typed-literal"
            and "langString" in binding["uri"]["datatype"]
        ):
            value = binding["uri"]["value"]
            allennlp_ner_output = ner.predict(sentence=value)
            if is_place(allennlp_ner_output) or is_person(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding["uri"]["type"] == "uri":
            value = extract_resource_name_from_uri(binding["uri"]["value"])
            allennlp_ner_output = ner.predict(sentence=value)
            if is_place(allennlp_ner_output) or is_person(allennlp_ner_output):
                filtered_bindings.append(binding)

    return {"bindings": filtered_bindings}


def filter_language(results):
    filtered_bindings = []
    value = ""
    for binding in results["bindings"]:
        if (
            binding["uri"]["type"] == "typed-literal"
            and "langString" in binding["uri"]["datatype"]
        ):
            value = binding["uri"]["value"]
            allennlp_ner_output = ner.predict(sentence=value)
            if "language" in value or is_language(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding["uri"]["type"] == "uri":
            value = extract_resource_name_from_uri(binding["uri"]["value"])
            allennlp_ner_output = ner.predict(sentence=value)
            if "language" in value or is_language(allennlp_ner_output):
                filtered_bindings.append(binding)

    return {"bindings": filtered_bindings}


def extract_type_names(uri):
    uri_path = urlparse(uri)
    if uri_path.fragment:
        name = uri_path.fragment
    else:
        name = os.path.basename(uri_path.path)

    p = re.compile(r"(_|\([^()]*\))")
    name = p.sub(" ", name)
    p2 = re.compile(r"([a-z0-9])([A-Z])")
    name = p2.sub(r"\1 \2", name)
    if not name.strip():
        return ""
    return name.lower()
