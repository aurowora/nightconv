app:
	cd front/; npm i; npm run build
	cp -R front/public .

clean:
	rm -R public