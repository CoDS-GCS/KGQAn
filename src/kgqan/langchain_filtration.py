import torch
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
import os
import re

os.environ["OPENAI_API_KEY"] = "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"
access_token = "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"
torch.set_default_tensor_type(torch.DoubleTensor)



def get_openAI_llm():
    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
    # llm = OpenAI(model_name="gpt-4", temperature=0)
    return llm


def get_name(predicate):
    pattern = r'[#/]([^/#]+)$'
    match = re.search(pattern, predicate)
    if match:
        name = match.group(1)
        # p2 = re.compile(r"([a-z0-9])([A-Z])")
        # name = p2.sub(r"\1 \2", name)
        return name
    else:
        return ""


def prepare_keywords_list(triples_list):
    predicate_to_query_id = {}
    output = ""
    for i, triples in enumerate(triples_list):
        for triple in triples:
            name = get_name(triple[1][0])
            if name != "":
                if name in predicate_to_query_id:
                    predicate_to_query_id[name].append(i)
                else:
                    predicate_to_query_id[name] = [i]
                    output += name + ', '
    return output[: len(output) - 2], predicate_to_query_id


def choose_question_from_keywords(question, query_list, triples_list):
    # 45 on qald, # best reults for solution 13(m)
    template = ("Task: Select all keywords from the provided list below that are relevant to answer the question: "
                "{question}\nList of Keywords:\n{predicate_list}\nInstructions: Please choose only the keywords from "
                "the list above that you believe are relevant to answering the question accurately. Ensure that the "
                "selected keywords belong to the provided list. If none of the keywords are applicable, return None.")

    prompt = PromptTemplate(
        input_variables=["question", "predicate_list"],
        template=template,
    )
    predicate_list, predicate_to_query_id = prepare_keywords_list(triples_list)
    final_prompt = prompt.format(question=question, predicate_list=predicate_list)
    print(final_prompt)
    llm = get_openAI_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    output = chain.run(question=question, predicate_list=predicate_list)
    print(output)
    return_result = list()
    # Parsing for solution 13 -m
    keywords = output.split(',')
    for k in keywords:
        k = k.strip()
        if k == "None":
            continue
        elif k in predicate_to_query_id:
            return_result.extend(predicate_to_query_id[k])
        else:
            print(f"Error {k} not in input list")

    return list(set(return_result))
