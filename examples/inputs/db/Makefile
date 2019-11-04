OUTFILE := tables.py

00: 00sqlite/db.sqlite
	python gen.py --db sqlite:///00sqlite/db.sqlite | tee `echo $@*`/${OUTFILE}

00sqlite/db.sqlite:
	cat 00sqlite/schema.sql | sqlite3 00sqlite/db.sqlite
clean:
	rm -f 00sqlite/db.sqlite
