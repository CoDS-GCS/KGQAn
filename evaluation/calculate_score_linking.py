import json

# file1_name = r"/home/ishika/Downloads/FullyAnnotated_LCQuAD5000.json"
# file2_name = r"/home/ishika/try1.json"
file1_name = r"/home/ishika/LCQuad_10ques.json"
file2_name = r"/home/ishika/LCQuad_10ques_fake.json"
file3_name = r"/home/ishika/LCQuad_10ques_fake2.json"

if __name__ == '__main__':
    # Predicate scores
    predicate_precision = list()
    predicate_recall = list()
    predicate_fmeasure = list()

    # Entity scores
    entity_precision = list()
    entity_recall = list()
    entity_fmeasure = list()

    # Common Evaluation metric
    precision = list()
    recall = list()
    f_measure = list()

    with open(file1_name) as f1:
        ground_truth = json.load(f1)

    with open(file2_name) as f2:
        produced = json.load(f2)

    with open(file3_name) as f2:
        produced2 = json.load(f2)


    def set_value(prec: float, rec: float, fscore: float):
        precision.append(prec)
        recall.append(rec)
        f_measure.append(fscore)


    def equals(real_dict, predicted_dict):
        return real_dict['label'] == predicted_dict['label'] and real_dict['uri'] == predicted_dict['uri']


    def evaluate_v2(real, predicted):
        if (len(real) == 0) and (len(predicted) == 0):
            set_value(1.0, 1.0, 1.0)
        elif (len(real) == 0) and (len(predicted) != 0):
            set_value(0, 0, 0)
        elif (len(real) != 0) and (len(predicted) == 0):
            set_value(0, 0, 0)
        else:
            hits = 0
            for r in range(len(real)):
                for p in range(len(predicted)):
                    if equals(real[r], predicted[p]):
                        hits += 1

            print("hits", hits)
            pre = hits / len(predicted)
            rec = hits / len(real)
            if (pre == 0) and (rec == 0):
                f_score = 0
            else:
                f_score = 2 * (pre * rec) / (pre + rec)
            print(pre, rec, f_score)
            set_value(pre, rec, f_score)


    def avg_score(r_value, p_value):
        evaluate_v2(r_value, p_value)
        precision_value = sum(precision) / len(precision)
        recall_value = sum(recall) / len(recall)
        fmeasure_value = sum(f_measure) / len(f_measure)
        return precision_value, recall_value, fmeasure_value


    def predicate_eval(r_predicate, p_predicate):
        precision_value, recall_value, fmeasure_value = avg_score(r_predicate, p_predicate)

        predicate_precision.append(precision_value)
        predicate_recall.append(recall_value)
        predicate_fmeasure.append(fmeasure_value)


    def entity_eval(r_entity, p_entity):
        precision_value, recall_value, fmeasure_value = avg_score(r_entity, p_entity)
        entity_precision.append(precision_value)
        entity_recall.append(recall_value)
        entity_fmeasure.append(fmeasure_value)


    for question in range(len(ground_truth)):
        real_predicate = []
        pred_predicate = []
        if (ground_truth[question]['SerialNumber']) == (produced[question]['SerialNumber']):
            # Fetch real predicate and entity mapping
            real_predicate = (ground_truth[question]['predicate mapping'])
            # Fetch predicted predicate mapping and entity mapping
            pred_predicate = (produced[question]['predicate mapping'])
            predicate_eval(real_predicate, pred_predicate)
        else:
            continue

    precision = list()
    recall = list()
    f_measure = list()

    for question in range(len(ground_truth)):
        real_entity = []
        pred_entity = []
        if (ground_truth[question]['SerialNumber']) == (produced[question]['SerialNumber']):
            real_entity = (ground_truth[question]['entity mapping'])  # Fetch real predicate and entity mapping
            pred_entity = (produced[question]['entity mapping'])  # Fetch predicted predicate mapping and entity mapping

            entity_eval(real_entity, pred_entity)
        else:
            continue
    print("Entity eval P =", entity_precision[-1], "R=", entity_recall[-1], "F =", entity_fmeasure[-1])
    print("Predicate eval P =", predicate_precision[-1], "R=", predicate_recall[-1], "F =", predicate_fmeasure[-1])