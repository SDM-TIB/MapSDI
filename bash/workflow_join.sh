
# to extract the attributes from sources
FILE=$1
ATTRIBUTE1=$2
ATTRIBUTE2=$3
OUTPUT=$4

colname1=$(head -n1 $FILE | tr "," "\n" | grep -n $ATTRIBUTE1 | cut -d ':' -f 1);
colname2=$(head -n1 $FILE | tr "," "\n" | grep -n $ATTRIBUTE2 | cut -d ':' -f 1);
sed 1d $FILE > $OUTPUT/temp.csv; 
mv $OUTPUT/temp.csv $FILE  ;  
cut -d, -f "$colname1","$colname2" $FILE | cat > $OUTPUT/attribute_column_temp1.csv

mv $OUTPUT/attribute_column.csv $OUTPUT/attribute_column_temp3.csv
cat $OUTPUT/attribute_column_temp1.csv $OUTPUT/attribute_column_temp3.csv > $OUTPUT/attribute_column.csv

