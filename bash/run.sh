OUTPUT=$1
HEADER1=$2
HEADER2=$3

# remove duplicates after merging
sort -u $OUTPUT/attribute_column.csv > $OUTPUT/attribute_column_wh.csv

# add header to the column
echo $HEADER1 > $OUTPUT/header1.csv
echo $HEADER2 > $OUTPUT/header2.csv
:|paste -d',' $OUTPUT/header1.csv $OUTPUT/header2.csv > $OUTPUT/header.csv
cat $OUTPUT/header.csv $OUTPUT/attribute_column_wh.csv > $OUTPUT/attribute_column_result.csv

# Run the rdfizer for the produced data based on the provided and mapping and configuration

# Run the rdfizer
#cp /resources/output/attribute_column_result.csv /bash

#cd /bash/
#java -jar /RDFizers/rmlmapper-java/rmlmapper-4.3.3-r92.jar -m /resources/transcript_rmlmapper.ttl -o /resources/output/transcript.nt

python3 /RDFizers/rdfizer_tib/rdfizer/rdfizer/run_rdfizer.py /home/jozashoori/External/Script/mapping/bash/conf.ini

