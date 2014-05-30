psql -Uwt_statistic -p5433 -dkjjy_LogAnalysis -h172.18.4.244 <<EOF
create table PV(
   id serial not null primary key,
   statistics_date timestamp without time zone,
   pvcount int
);
create table UV(
   id serial not null primary key,
   statistics_date timestamp without time zone,
   uvcount int
);
create table urlcount( 
   id serial not null primary key, 
   statistics_date timestamp without time zone, 
   url varchar(200), 
   count integer
);
EOF
