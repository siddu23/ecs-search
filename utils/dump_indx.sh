set -x

rm *.gz

tar -xvf author.tar
tar -xvf pratilipi.tar

gunzip author*
gunzip pratilipi*

curl "http://localhost:8983/solr/author/update?stream.body=<delete><query>*:*</query></delete>&commit=true"
curl "http://localhost:8983/solr/pratilipi/update?stream.body=<delete><query>*:*</query></delete>&commit=true"

curl "http://localhost:8983/solr/author/select?q=*"
curl "http://localhost:8983/solr/pratilipi/select?q=*"

for i in `ls author_data*.json`; do echo $i; ~/solr/bin/post -c author $i; done
for i in `ls pratilipi_data*.json`; do echo $i; ~/solr/bin/post -c pratilipi $i; done

curl "http://localhost:8983/solr/author/select?q=*"
curl "http://localhost:8983/solr/pratilipi/select?q=*"

