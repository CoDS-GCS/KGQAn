import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import io
from kgqan import KGQAn

hostName = "0.0.0.0"
serverPort = 8899

max_Vs = 1
max_Es = 10
max_answers = 41
limit_VQuery = 100
limit_EQuery = 100

class MyServer(BaseHTTPRequestHandler):

    def running_example_answer(self):
        objs=[]
        obj1 = {'question': 'When did the Boston Tea Party take place and Who was it led by?',
                'sparql': 'SELECT * WHERE { <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/date> ?When . <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/leadfigures> ?whom }',
                'values': [
                    '1773-12-16    http://dbpedia.org/resource/East_India_Company',
                    '1773-12-16    http://dbpedia.org/resource/Paul_Revere',
                    '1773-12-16    http://dbpedia.org/resource/William_Molineux',
                    '1773-12-16    http://dbpedia.org/resource/British_Parliament',
                    '1773-12-16    http://dbpedia.org/resource/Samuel_Adams'],
                'named_entites': ['Boston Tea Party'],
                'extracted_relation': [['Boston Tea Party', "?when", 'take place'], [['Boston Tea Party', "?who", 'led by']]],
                'score': 1,
                "nodes": ['http://dbpedia.org/resource/Boston_Tea_Party'],
                'edges': ['<http://dbpedia.org/property/date>',
                          '<http://dbpedia.org/property/leadfigures>']}
        objs.append(obj1)
        obj2 = {'question': 'When did the Boston Tea Party take place and Who was it led by?',
                'sparql': 'SELECT * WHERE { <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/date> ?When . <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/leadfigures> ?whom .}',
                'values': [
                    'Boston, Massachusetts, British America    http://dbpedia.org/resource/East_India_Company',
                    'Boston, Massachusetts, British America   http://dbpedia.org/resource/Paul_Revere',
                    'Boston, Massachusetts, British America    http://dbpedia.org/resource/William_Molineux',
                    'Boston, Massachusetts, British America    http://dbpedia.org/resource/British_Parliament',
                    'Boston, Massachusetts, British America   http://dbpedia.org/resource/Samuel_Adams'],
                'named_entites': ['Boston Tea Party'],
                'extracted_relation': [['Boston Tea Party', "?when", 'take place'],
                                       [['Boston Tea Party', "?who", 'led by']]],
                'score': 1,
                "nodes": ['http://dbpedia.org/resource/Boston_Tea_Party'],
                'edges': ['<http://dbpedia.org/property/place>',
                          '<http://dbpedia.org/property/leadfigures>']}
        objs.append(obj2)
        return json.dumps(objs)

    def parse_answer(self, answers, entities, max_answers, edges):
        nodes = []
        if len(entities) != 0:
            nodes = list(entities)

        relations = []
        if len(edges) != 0:
            relations = list(edges(data='relation'))
        if 'uri' in nodes:
            nodes.remove('uri')
        objs = []
        for answer in answers:
            values = []
            if answer['results'] and answer['results']['bindings']:
                for value in answer['results']['bindings']:
                    values.append(value['uri']['value'])
            if len(values) > 0:
                obj = {'question': answer['question'], 'sparql': answer['sparql'], 'values': values, 'named_entites': nodes,
                       'extracted_relation': relations, 'score': answer['score'], "nodes": answer['nodes'],
                       'edges': answer['edges']}
                objs.append(obj)

            if len(objs) == max_answers:
                break

        return json.dumps(objs)

    def do_POST(self):
        print("In post ")
        print(self.request)
        try:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            print("Before parsing ", post_data)
            # fix_bytes_value = post_data.replace(b"'", b'"')
            data = json.load(io.BytesIO(post_data))
            print("After parsing ", data)
        except:
            self.send_error(500, "Failed to parse data from request")

        try:
            MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                            n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery)
            # TODO should be removed
            if data['question'] == 'When did the Boston Tea Party take place and who was it led by?':
                result = self.running_example_answer()
            else:
                answers, entities, edges = MyKGQAn.ask(question_text=data['question'], knowledge_graph=data['knowledge_graph'])
                result = self.parse_answer(answers, entities, data['max_answers'], edges)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(result, "utf-8"))
        except Exception as e:
            print("Error from : ", e)
            print("Stack trace")
            traceback.print_exc()
            self.send_error(500, "Failed to get the answer to the question")

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
