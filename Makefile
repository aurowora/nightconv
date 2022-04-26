app:
	cd front/; npm run build
	cp -R front/public .

clean:
	rm -R public