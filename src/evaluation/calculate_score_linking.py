import json
import os
import csv

file_dir = os.path.dirname(os.path.abspath(__file__))

ground_truth = os.path.join(file_dir, "lcquad1/FullyAnnotated_LCQuAD5000.json")
predictions = os.path.join(file_dir, "output/FilteringLinkingquesBoolean.json")
#
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

    with open(ground_truth) as f1:
        ground_truth = json.load(f1)

    with open(predictions) as f2:
        produced = json.load(f2)


    def set_value(prec: float, rec: float, fscore: float):
        precision.append(prec)
        recall.append(rec)
        f_measure.append(fscore)


    def equals(real_dict, predicted_dict):
        # print("real_dict uri = ", real_dict['uri'])
        # print("pred_dict uri = ", predicted_dict['uri'].replace('<', "").replace('>', ""))
        return real_dict['uri'] == predicted_dict['uri'].replace('<', "").replace('>', "")
        # or predicted_dict['uri'].replace('<', "").replace('>', "") in real_dict['uri']

        # return real_dict['label'] == predicted_dict['label'] or predicted_dict['label'] in real_dict['label'] and \
        #        real_dict['uri'] == predicted_dict['uri']


    def evaluate(real, predicted):
        hit_ques = 0
        if (len(real) == 0) and (len(predicted) == 0):
            set_value(1.0, 1.0, 1.0)
        elif (len(real) == 0) and (len(predicted) != 0):
            set_value(0, 0, 0)
        elif (len(real) != 0) and (len(predicted) == 0):
            set_value(0, 0, 0)
        else:
            hits = 0
            # for r in range(len(real)):
            #     for p in range(len(predicted)):
            #         # print("Real", real[r])
            #         # print("pred",predicted[p])
            #         if equals(real[r], predicted[p]):
            #             hits += 1
            for r in range(len(real)):
                for p in range(len(predicted)):
                    # if len(real[r]) == 2 and len(predicted[p]) == 2:
                    if len(real[r]) == 2 and len(predicted[p]) > 0:
                        if equals(real[r], predicted[p]):
                            hits += 1
                    elif len(real[r]) == 0 or len(predicted[p]) != 0:
                        hits = 0
                    elif len(real[r]) != 0 or len(predicted[p]) == 0:
                        hits = 0
                    elif len(real[r]) == 0 or len(predicted[p]) == 0:
                        set_value(1.0, 1.0, 1.0)
            pre = hits / len(predicted)
            rec = hits / len(real)
            if (pre == 0) and (rec == 0):
                f_score = 0
            else:
                f_score = 2 * (pre * rec) / (pre + rec)
            set_value(pre, rec, f_score)


    def avg_score(r_value, p_value):
        evaluate(r_value, p_value)
        precision_value = sum(precision) / len(precision)
        recall_value = sum(recall) / len(recall)
        f_value = sum(f_measure) / len(f_measure)
        return precision_value, recall_value, f_value


    def predicate_eval(r_predicate, p_predicate):
        precision_value, recall_value, f2measure_value = avg_score(r_predicate, p_predicate)

        predicate_precision.append(precision_value)
        predicate_recall.append(recall_value)
        predicate_fmeasure.append(f2measure_value)


    def entity_eval(r_entity, p_entity):
        precision_value, recall_value, f1measure_value = avg_score(r_entity, p_entity)
        entity_precision.append(precision_value)
        entity_recall.append(recall_value)
        entity_fmeasure.append(f1measure_value)


    #
    # for question in range(len(produced)):
    #     # count += 1
    #     real_predicate = []
    #     pred_predicate = []
    #     # print(ground_truth[question]['question'])
    #     # print(produced[question]['question'])
    #
    #     if (ground_truth[question]['question']) == (produced[question]['question']):
    #         # print("GT question for predicates", ground_truth[question]["question"])
    #         real_predicate = (ground_truth[question]['predicate mapping'])  # Fetch real predicate and entity mapping
    #         pred_predicate = (produced[question]['predicate mapping'])  # Fetch predicted predicate mapping and entity
    #         # mapping
    #         predicate_eval(real_predicate, pred_predicate)
    #     else:
    #         continue
    #
    # precision = list()
    # recall = list()
    # f_measure = list()
    #
    # for question in range(len(produced)):
    #     real_entity = []
    #     pred_entity = []
    #     if (ground_truth[question]['SerialNumber']) == (produced[question]['SerialNumber']):
    #         # print("GT question for entities", ground_truth[question]["question"])
    #         real_entity = (ground_truth[question]['entity mapping'])  # Fetch real predicate and entity mapping
    #         pred_entity = (produced[question]['entity mapping'])  # Fetch predicted predicate mapping and entity mapping
    #
    #         entity_eval(real_entity, pred_entity)
    #     else:
    #         continue
    # # print("Entity eval P =", entity_precision, "R=", entity_recall, "F =", entity_fmeasure)
    # # print("Predicate eval P =", predicate_precision, "R=", predicate_recall[-1], "F =", predicate_fmeasure[-1])
    #
    # q = ["Name the municipality of Roberto Clemente Bridge ?"]
    # for i in range(len(q)):
    #     for q1 in range(len(produced)):
    #         for q2 in range(len(ground_truth)):
    #             if (produced[q1]['question']) == (ground_truth[q2]['question']) == q[i]:
    #                 real_predicate = (ground_truth[q2]['predicate mapping'])
    #                 pred_predicate = (produced[q1]['predicate mapping'])
    #
    #                 predicate_eval(real_predicate, pred_predicate)
    #
    # precision = list()
    # recall = list()
    # f_measure = list()
    # for i in range(len(q)):
    #     for q1 in range(len(produced)):
    #         for q2 in range(len(ground_truth)):
    #             if (produced[q1]['question']) == (ground_truth[q2]['question']) == q[i]:
    #                 real_entity = (ground_truth[q2]['entity mapping'])
    #                 pred_entity = (produced[q1]['entity mapping'])
    #
    #                 entity_eval(real_entity, pred_entity)
    #                 #
    # print("Predicate eval P =", predicate_precision[-1], "R=", predicate_recall[-1], "F =", predicate_fmeasure[-1])
    # print("entity eval P =", entity_precision[-1], "R=", entity_recall[-1], "F =", entity_fmeasure[-1])
    # print("\nPredicate eval P =", predicate_precision, "R=", predicate_recall, "F =", predicate_fmeasure)
    # print("entity eval P =", entity_precision, "R=", entity_recall, "F =", entity_fmeasure)
    # #
    #

    # actual file evaluate
    i = 0
    for question1 in range(len(produced)):
        # print("q", produced[question1]['question'])
        for question2 in range(len(ground_truth)):
            if (produced[question1]['question']) in (ground_truth[question2]['question']):
                i += 1
                real_predicate = (ground_truth[question2]['predicate mapping'])  # Fetch real predicate mapping
                pred_predicate = (produced[question1]['predicate mapping'])  # Fetch predicted predicate mapping
                predicate_eval(real_predicate, pred_predicate)

    precision = list()
    recall = list()
    f_measure = list()
    count = 0
    # actual file evaluate
    for question1 in range(len(produced)):
        # if count == 6:
        #     break
        for question2 in range(len(ground_truth)):
            if (produced[question1]['question']) in (ground_truth[question2]['question']):
                count += 1
                real_entity = (ground_truth[question2]['entity mapping'])  # Fetch real entity
                pred_entity = (produced[question1]['entity mapping'])  # Fetch predicted entity
                entity_eval(real_entity, pred_entity)

    print("Predicate eval P =", predicate_precision[-1], "R=", predicate_recall[-1], "F =", predicate_fmeasure[-1])
    print("entity eval P =", entity_precision[-1], "R=", entity_recall[-1], "F =", entity_fmeasure[-1])
    # print("count", count)
    # print("i", i)
    results = [["Entity Linking"], ["P", "R", "F1"], [entity_precision[-1]*100, entity_recall[-1]*100, entity_fmeasure[-1]*100],
               ["Relation Linking"], ["P", "R", "F1"], [predicate_precision[-1]*100, predicate_recall[-1]*100, predicate_fmeasure[-1]*100]]

    file_path = 'output/evaluation_results.csv'
    with open(os.path.join(file_dir,file_path), mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for row in results:
            writer.writerow(row)


