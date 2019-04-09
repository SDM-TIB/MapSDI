import re
import csv
import sys
import rdflib
from triples_map import TriplesMap as tm
from rdflib.plugins.sparql import prepareQuery
import time
import subprocess
import os
import pandas as pd
###############################################

def mapping_parser(mapping_file):
	"""
	(Private function, not accessible from outside this package)

	Takes a mapping file in Turtle (.ttl) or Notation3 (.n3) format and parses it into a list of
	TriplesMap objects (refer to TriplesMap.py file)

	Parameters
	----------
	mapping_file : string
		Path to the mapping file

	Returns
	-------
	A list of TriplesMap objects containing all the parsed rules from the original mapping file
	"""
	mapping_graph = rdflib.Graph()


	try:
		mapping_graph.load(mapping_file, format='n3')
	except Exception as n3_mapping_parse_exception:
		print(n3_mapping_parse_exception)
		print('Could not parse {} as a mapping file'.format(mapping_file))
		print('Aborting...')
		sys.exit(1)


	mapping_query = """
		prefix rr: <http://www.w3.org/ns/r2rml#> 
		prefix rml: <http://semweb.mmlab.be/ns/rml#> 
		prefix ql: <http://semweb.mmlab.be/ns/ql#> 
		SELECT DISTINCT *
		WHERE {

	# Subject -------------------------------------------------------------------------
			?triples_map_id rml:logicalSource ?_source .
			?_source rml:source ?data_source .
			?_source rml:referenceFormulation ?ref_form .
			OPTIONAL { ?_source rml:iterator ?iterator . }
			
			?triples_map_id rr:subjectMap ?_subject_map .
			?_subject_map rr:template ?subject_template .
			OPTIONAL { ?_subject_map rr:class ?rdf_class . }
	# Predicate -----------------------------------------------------------------------
			OPTIONAL {
			?triples_map_id rr:predicateObjectMap ?_predicate_object_map .
			}
			OPTIONAL {
				?triples_map_id rr:predicateObjectMap ?_predicate_object_map .
				?_predicate_object_map rr:predicateMap ?_predicate_map .
				?_predicate_map rr:constant ?predicate_constant .
			}
			OPTIONAL {
				?_predicate_object_map rr:predicateMap ?_predicate_map .
				?_predicate_map rr:template ?predicate_template .
			}
			OPTIONAL {
				?_predicate_object_map rr:predicateMap ?_predicate_map .
				?_predicate_map rml:reference ?predicate_reference .
			}
			OPTIONAL {
				?_predicate_object_map rr:predicate ?predicate_constant_shortcut .
			}

	# Object --------------------------------------------------------------------------
			OPTIONAL {
				?_predicate_object_map rr:objectMap ?_object_map .
				?_object_map rr:constant ?object_constant .
				OPTIONAL {
					?_object_map rr:datatype ?object_datatype .
				}
			}
			OPTIONAL {
				?_predicate_object_map rr:objectMap ?_object_map .
				?_object_map rr:template ?object_template .
				OPTIONAL {
					?_object_map rr:datatype ?object_datatype .
				}
			}
			OPTIONAL {
				?_predicate_object_map rr:objectMap ?_object_map .
				?_object_map rml:reference ?object_reference .
				OPTIONAL {
					?_object_map rr:datatype ?object_datatype .
				}
			}
			OPTIONAL {
				?_predicate_object_map rr:objectMap ?_object_map .
				?_object_map rr:parentTriplesMap ?object_parent_triples_map .
				OPTIONAL {
					?_object_map rr:joinCondition ?join_condition .
					?join_condition rr:child ?child_value;
								 rr:parent ?parent_value.
				}
				OPTIONAL {
					?_object_map rr:joinCondition ?join_condition .
					?join_condition rr:child ?child_value;
								 rr:parent ?parent_value;
				}
			}
			OPTIONAL {
				?_predicate_object_map rr:object ?object_constant_shortcut .
				OPTIONAL {
					?_object_map rr:datatype ?object_datatype .
				}
			}
		} """
	mapping_query_results = mapping_graph.query(mapping_query)
	triples_map_list = []


	for result_triples_map in mapping_query_results:
		triples_map_exists = False
		for triples_map in triples_map_list:
			triples_map_exists = triples_map_exists or (str(triples_map.triples_map_id) == str(result_triples_map.triples_map_id))
		
		if not triples_map_exists:
			if result_triples_map.rdf_class is None:
				reference, condition = string_separetion(str(result_triples_map.subject_template))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_template), condition, result_triples_map.rdf_class)
			else:
				reference, condition = string_separetion(str(result_triples_map.subject_template))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_template), condition, str(result_triples_map.rdf_class))
				
			mapping_query_prepared = prepareQuery(mapping_query)


			mapping_query_prepared_results = mapping_graph.query(mapping_query_prepared, initBindings={'triples_map_id': result_triples_map.triples_map_id})


			predicate_object_maps_list = []


			for result_predicate_object_map in mapping_query_prepared_results:
				if result_predicate_object_map.predicate_constant is not None:
					predicate_map = tm.PredicateMap("constant", str(result_predicate_object_map.predicate_constant), "")
				elif result_predicate_object_map.predicate_constant_shortcut is not None:
					predicate_map = tm.PredicateMap("constant shortcut", str(result_predicate_object_map.predicate_constant_shortcut), "")
				elif result_predicate_object_map.predicate_template is not None:
					template, condition = string_separetion(str(result_predicate_object_map.predicate_template))
					predicate_map = tm.PredicateMap("template", template, condition)
				elif result_predicate_object_map.predicate_reference is not None:
					reference, condition = string_separetion(str(result_predicate_object_map.predicate_reference))
					predicate_map = tm.PredicateMap("reference", reference, condition)
				else:
					print("Invalid predicate map")
					print("Aborting...")
					sys.exit(1)

				if result_predicate_object_map.object_constant is not None:
					object_map = tm.ObjectMap("constant", str(result_predicate_object_map.object_constant), str(result_predicate_object_map.object_datatype), "None", "None")
				elif result_predicate_object_map.object_template is not None:
					object_map = tm.ObjectMap("template", str(result_predicate_object_map.object_template), str(result_predicate_object_map.object_datatype), "None", "None")
				elif result_predicate_object_map.object_reference is not None:
					object_map = tm.ObjectMap("reference", str(result_predicate_object_map.object_reference), str(result_predicate_object_map.object_datatype), "None", "None")
				elif result_predicate_object_map.object_parent_triples_map is not None:
					object_map = tm.ObjectMap("parent triples map", str(result_predicate_object_map.object_parent_triples_map), str(result_predicate_object_map.object_datatype), str(result_predicate_object_map.child_value), str(result_predicate_object_map.parent_value))
				elif result_predicate_object_map.object_constant_shortcut is not None:
					object_map = tm.ObjectMap("constant shortcut", str(result_predicate_object_map.object_constant_shortcut), str(result_predicate_object_map.object_datatype), "None", "None")
				else:
					print("Invalid object map")
					print("Aborting...")
					sys.exit(1)

				predicate_object_maps_list += [tm.PredicateObjectMap(predicate_map, object_map)]

			current_triples_map = tm.TriplesMap(str(result_triples_map.triples_map_id), str(result_triples_map.data_source), subject_map, predicate_object_maps_list, ref_form=str(result_triples_map.ref_form), iterator=str(result_triples_map.iterator))
			triples_map_list += [current_triples_map]

	return triples_map_list

def string_separetion(string):
	if ("{" in string) and ("[" in string):
		prefix = string.split("{")[0]
		condition = string.split("{")[1].split("}")[0]
		postfix = string.split("{")[1].split("}")[1]
		field = prefix + "*" + postfix
	elif "[" in string:
		return string, string
	else:
		return string, ""
	return string, condition


def handler():

	#start = time.time()
	#path = "/Users/sam/Desktop/ISWC/test/mappings/"
	path = sys.argv[1] 
	output = sys.argv[2]
	source_attribute = dict()
	source_column = dict()
	concept_list = []
	dup_list = []
	column_result = dict()

	for file in os.listdir(path):
		mapping_list=mapping_parser(path+file)
		for item in mapping_list:
			source = item.data_source
			sub_class = item.subject_map.rdf_class
			column = item.subject_map.value.split("{")[1].split("}")[0]
			l = len(str(sub_class).split("/"))
			concept = str(sub_class).split("/")[l-1]
			if concept in concept_list:
				dup_list.append(concept)
			else:
				concept_list.append(concept)
			source_attribute[source] = concept
			source_column[source] = column

	for k,v in source_attribute.items():
		if v in dup_list:
			header=v
			column_result[k]=source_column[k]

	for k,v in column_result.items():
		argValue = " " + str(k) + " " + str(v) + " " + output
		bashCommand = "/home/jozashoori/External/Script/mapping/bash/workflow.sh" + argValue
		subprocess.call(bashCommand, shell=True)	
	runBash = "/home/jozashoori/External/Script/mapping/bash/run.sh" + " " + output + " " + header	
	subprocess.call(runBash, shell=True)	

	#end = time.time()
	#print("time:")
	#print(end-start)	

if __name__ == "__main__":
        handler()