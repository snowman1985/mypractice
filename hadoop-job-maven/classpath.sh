

for file in ./lib/*.jar
do
  CLASSPATH=$CLASSPATH:$file
done

echo $CLASSPATH
