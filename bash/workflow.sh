
# to extract the attributes from sources
FILE=$1
ATTRIBUTE=$2
OUTPUT=$3

colname=$(head -n1 $FILE | tr "," "\n" | grep -n $ATTRIBUTE | cut -d ':' -f 1);
sed 1d $FILE > $OUTPUT/temp.csv; 
mv $OUTPUT/temp.csv $FILE  ;  
cut -d, -f "$colname" $FILE | cat > $OUTPUT/attribute_column_temp1.csv
mv $OUTPUT/attribute_column.csv $OUTPUT/attribute_column_temp2.csv
cat $OUTPUT/attribute_column_temp1.csv $OUTPUT/attribute_column_temp2.csv > $OUTPUT/attribute_column.csv

