set -x

rm *.json
rm *.gz
rm *.tar

. /home/gauri/search/venv/bin/activate
python /home/gauri/codebase/ecs-search/src/fileuploader.py

cd /home/gauri/Downloads/solr_data/
gunzip *_solr.json.gz

split -l 10000 author_solr.json author_data_
split -l 10000 pratilipi_solr.json pratilipi_data_

for i in `ls author_data_*`; do echo $i; mv $i $i.json; done
for i in `ls pratilipi_data_*`; do echo $i; mv $i $i.json; done

gzip author_data_*
gzip pratilipi_data_*

tar -cvf author.tar author_data_*.json.gz
tar -cvf pratilipi.tar pratilipi_data_*.json.gz

scp author.tar gamma-solr:/tmp/data/
scp pratilipi.tar gamma-solr:/tmp/data/

deactivate
